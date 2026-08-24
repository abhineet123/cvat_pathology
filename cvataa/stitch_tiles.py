import os
import re
import cv2
from tqdm import tqdm
from collections import defaultdict

import numpy as np
import tifffile
import openslide

import re
import csv

import paramparse

from cell_seg_utils import (
    linux_path,
    draw_box,
    overlay_cells,
)

CUPY_AVAILABLE = False
cp = None


class Params(paramparse.CFG):
    """
    Stitch QuPath-exported tiles for every prefix in a folder into full-resolution TIFFs.

    :ivar compression: TIFF compression. Default: none
    :type compression: str

    :ivar output_dir: Folder to save stitched TIFF files. Default: {tile_dir}-stitched
    :type output_dir: str

    :ivar prefix: Specific prefix (or filename) to stitch. If omitted, all prefixes are stitched.
    :type prefix: str

    :ivar tile_dir: Folder containing tile images. Default: empty
    :type tile_dir: str

    :ivar wsi_path: Path to wsi
    :type wsi_path: str

    :ivar save_metadata: Save tile metadata CSV alongside output TIFF. Default: 1 (on)
    :type save_metadata: int

    :ivar vis: factor by which to resize the wsi for real-time visualization (0 to disable real-time visualization)
    :type vis: int

    :ivar is_mask: Remap cell RGB IDs to be globally unique across tiles. Default: 1 (on)
    :type is_mask: int

    :ivar gpu: Use GPU via CuPy if available. Default: 1 (on). Set to 0 to force CPU.
    :type gpu: int

    """

    def __init__(self):
        paramparse.CFG.__init__(self)

        # self.compression = "none"
        self.compression = "zlib"
        self.output_dir = ""
        self.tile_dir = ""
        self.wsi_path = ""
        self.prefix = ""
        self.save_metadata = 0
        self.memmap = 1
        self.is_mask = 1
        # self.alpha = 0.25
        self.alpha = 1.0
        self.save = 1
        self.vis = 0
        self.gpu = 0


def try_init_cupy():
    global cp, CUPY_AVAILABLE
    try:
        import cupy as cp_module

        _ = cp_module.array([1, 2, 3])
        cp = cp_module
        CUPY_AVAILABLE = True
        print("CuPy initialized — GPU acceleration enabled.")
    except Exception as e:
        cp = None
        CUPY_AVAILABLE = False
        print(f"CuPy unavailable ({e}) — falling back to CPU.")


FILENAME_RE = re.compile(
    r"^(?P<prefix>.+?)\s*\[x=(?P<x>-?\d+),y=(?P<y>-?\d+),w=(?P<w>\d+),h=(?P<h>\d+)\]\.(?P<ext>png|jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)


def resolve_prefix(requested, available_prefixes):
    if requested in available_prefixes:
        return requested

    m = FILENAME_RE.match(requested)
    if m:
        candidate = m.group("prefix").strip()
        if candidate in available_prefixes:
            return candidate

    candidate = re.sub(r"\.tiff?$", "", requested, flags=re.IGNORECASE).strip()
    if candidate in available_prefixes:
        return candidate

    raise ValueError(
        f"Prefix {requested!r} not found.\n" f"Available prefixes: {sorted(available_prefixes)}"
    )


def collect_groups(tiles, enforce_unity=False):
    groups = defaultdict(list)

    if isinstance(tiles, str):
        tiles = [
            linux_path(tiles, fname)
            for fname in os.listdir(tiles)
            if os.path.isfile(linux_path(tiles, fname))
        ]

    for tile_path in tiles:
        tile_name = os.path.basename(tile_path)
        match = FILENAME_RE.match(tile_name)
        if not match:
            raise AssertionError(f"invalid tile_name: {tile_name}")

        prefix = match.group("prefix").strip()
        x = int(match.group("x"))
        y = int(match.group("y"))
        w = int(match.group("w"))
        h = int(match.group("h"))

        groups[prefix].append(
            {
                "fname": tile_name,
                "path": tile_path,
                "x": x,
                "y": y,
                "w_meta": w,
                "h_meta": h,
            }
        )

    if enforce_unity:
        tiles_prefixes = list(groups.keys())
        assert len(groups) == 1, f"multiple tile prefixes found: {tiles_prefixes}"

    if not groups:
        raise FileNotFoundError(
            f"No tile files matching the expected QuPath pattern were found in: {tiles}"
        )

    for prefix in groups:
        groups[prefix] = sorted(groups[prefix], key=lambda t: (t["y"], t["x"], t["fname"]))

    if enforce_unity:
        return next(iter(groups.values()))

    return groups


def save_metadata_csv(prefix, tiles, tile_w, tile_h, canvas_w, canvas_h, min_x, min_y, output_dir):
    csv_path = os.path.join(output_dir, f"{prefix}_tile_metadata.csv")
    fieldnames = [
        "fname",
        "path",
        "x",
        "y",
        "w_meta",
        "h_meta",
        "actual_w",
        "actual_h",
        "canvas_w",
        "canvas_h",
        "min_x",
        "min_y",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for t in tiles:
            writer.writerow(
                {
                    "fname": t["fname"],
                    "path": t["path"],
                    "x": t["x"],
                    "y": t["y"],
                    "w_meta": t["w_meta"],
                    "h_meta": t["h_meta"],
                    "actual_w": tile_w,
                    "actual_h": tile_h,
                    "canvas_w": canvas_w,
                    "canvas_h": canvas_h,
                    "min_x": min_x,
                    "min_y": min_y,
                }
            )
    print(f"Tile metadata saved: {csv_path}")


def read_image(path):
    arr = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if arr is None:
        raise IOError(f"cv2 could not read: {path}")
    if arr.ndim == 3 and arr.shape[2] >= 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
    return arr


def get_black_value(arr):
    if arr.ndim == 2:
        return 0
    elif arr.ndim == 3:
        return np.zeros(arr.shape[2], dtype=arr.dtype)
    else:
        raise ValueError(f"Unsupported array shape: {arr.shape}")


def remap_tile_cpu(mask_rgb, max_cell_id):
    """
    Vectorized RGB -> offset ID -> RGB remapping using numpy (CPU).
    Avoids full pixel scan for max by computing it from the RGB encoding directly.
    """
    ids = (
        mask_rgb[:, :, 0].astype(np.int32) * 65536
        + mask_rgb[:, :, 1].astype(np.int32) * 256
        + mask_rgb[:, :, 2].astype(np.int32)
    )

    nonblack = ids > 0

    if not nonblack.any():
        return mask_rgb, max_cell_id

    # Use max of encoded IDs directly — no extra pixel scan needed
    tile_max_id = int(ids.max())
    ids[nonblack] += max_cell_id
    new_max_cell_id = max_cell_id + tile_max_id

    mask_offset = np.zeros((*ids.shape, 3), dtype=np.uint8)
    mask_offset[:, :, 0] = (ids >> 16) & 0xFF
    mask_offset[:, :, 1] = (ids >> 8) & 0xFF
    mask_offset[:, :, 2] = ids & 0xFF

    return mask_offset, new_max_cell_id


def remap_tile_gpu(mask_rgb, max_cell_id):
    """
    Vectorized RGB -> offset ID -> RGB remapping using CuPy (GPU).
    """
    mask_gpu = cp.asarray(mask_rgb)

    ids = (
        mask_gpu[:, :, 0].astype(cp.int32) * 65536
        + mask_gpu[:, :, 1].astype(cp.int32) * 256
        + mask_gpu[:, :, 2].astype(cp.int32)
    )

    nonblack = ids > 0

    if not nonblack.any():
        return mask_rgb, max_cell_id

    tile_max_id = int(ids.max().get())
    ids[nonblack] += max_cell_id
    new_max_cell_id = max_cell_id + tile_max_id

    mask_offset_gpu = cp.zeros((*ids.shape, 3), dtype=cp.uint8)
    mask_offset_gpu[:, :, 0] = (ids >> 16) & 0xFF
    mask_offset_gpu[:, :, 1] = (ids >> 8) & 0xFF
    mask_offset_gpu[:, :, 2] = ids & 0xFF

    return cp.asnumpy(mask_offset_gpu), new_max_cell_id


def remap_tile(mask_rgb, max_cell_id):
    if CUPY_AVAILABLE:
        return remap_tile_gpu(mask_rgb, max_cell_id)
    return remap_tile_cpu(mask_rgb, max_cell_id)


def stitch_group(prefix, tiles, wsi: openslide.OpenSlide, params: Params):
    print("\n" + "=" * 80)
    print(f"Processing prefix: {prefix}")
    print(f"Tiles found: {len(tiles)}")
    print(f"Mode: {'GPU' if CUPY_AVAILABLE else 'CPU'}")

    first_arr = read_image(tiles[0]["path"])
    first_shape = first_arr.shape
    first_dtype = first_arr.dtype

    wsi_w, wsi_h = wsi.dimensions
    print(f"WSI dimensions: {wsi_w} x {wsi_h}")

    if first_arr.ndim == 2:
        tile_h, tile_w = first_arr.shape
        stitched_shape = (wsi_h, wsi_w)
        channels = None
    elif first_arr.ndim == 3:
        tile_h, tile_w, channels = first_arr.shape
        stitched_shape = (wsi_h, wsi_w, channels)
    else:
        raise ValueError(f"Unsupported image shape for {tiles[0]['fname']}: {first_shape}")

    print(f"First tile: {tiles[0]['fname']}")
    print(f"Detected tile size from file: {tile_w} x {tile_h}")

    if tile_w != tiles[0]["w_meta"] or tile_h != tiles[0]["h_meta"]:
        print(
            f"Warning: filename metadata says {tiles[0]['w_meta']}x{tiles[0]['h_meta']}, "
            f"but actual tile is {tile_w}x{tile_h}. Using actual tile size."
        )

    min_x = min(t["x"] for t in tiles)
    min_y = min(t["y"] for t in tiles)
    max_x = max(t["x"] + tile_w for t in tiles)
    max_y = max(t["y"] + tile_h for t in tiles)

    # canvas_w = max_x - min_x
    # canvas_h = max_y - min_y

    # print(f"Output image size: {canvas_w} x {canvas_h}")

    canvas_w, canvas_h = wsi_w, wsi_h

    if params.save_metadata:
        save_metadata_csv(
            prefix, tiles, tile_w, tile_h, wsi_w, wsi_h, min_x, min_y, params.output_dir
        )

    if params.vis:
        vis_w = canvas_w // params.vis
        vis_h = canvas_h // params.vis
        tile_h_vis = tile_h // params.vis
        tile_w_vis = tile_w // params.vis
        print(f"vis image size: {vis_w} x {vis_h}")
        stitched_vis = np.zeros((vis_h, vis_w, 3), dtype=np.uint8)

    # expected_cols = math.ceil(canvas_w / tile_w)
    # expected_rows = math.ceil(canvas_h / tile_h)
    # expected_slots = expected_cols * expected_rows
    # missing_estimate = expected_slots - len(tiles)

    # print(f"Estimated grid: {expected_cols} cols x {expected_rows} rows")
    # if missing_estimate > 0:
    #     print(f"Estimated missing tile slots: {missing_estimate}")
    #     print("Missing regions will remain black.")

    if params.save:
        print("initializing stitched array")
        if params.memmap:
            memmap_path = os.path.join(params.output_dir, f"{prefix}.memmap")
            stitched = np.memmap(memmap_path, dtype=first_dtype, mode="w+", shape=stitched_shape)
        else:
            stitched = np.zeros(stitched_shape, dtype=first_dtype)
        stitched[...] = get_black_value(first_arr)

    max_cell_id = 0

    pbar = tqdm(enumerate(tiles, start=1), total=len(tiles))

    pause = 1

    for i, t in pbar:
        try:
            tile_img = read_image(t["path"])
        except Exception as e:
            raise AssertionError(f"could not read {t['fname']}: {e}")

        if tile_img.shape != first_shape:
            raise AssertionError(f"invalid file {t['fname']} with shape mismatch: {tile_img.shape}")

        if params.is_mask:
            tile_img, max_cell_id = remap_tile(tile_img, max_cell_id)
            pbar.set_description(f"max_cell_id: {max_cell_id}")

        x = t["x"]
        y = t["y"]
        if params.save:
            stitched[y : y + tile_h, x : x + tile_w, ...] = tile_img

        if x < 0 or y < 0 or x + tile_w > wsi_w or y + tile_h > wsi_h:
            raise AssertionError(f"Out of bounds tile: {t['fname']}")

        if params.vis:
            if params.is_mask:
                wsi_tile = wsi.read_region(location=(x, y), level=0, size=(tile_w, tile_h))
                wsi_tile_np = np.array(wsi_tile)[..., :3]

                wsi_tile_overlaid = overlay_cells(wsi_tile_np, tile_img, params.alpha)

                # cell_mask = tile_img > 0
                # wsi_tile_overlaid = np.copy(wsi_tile_np)
                # wsi_tile_overlaid[cell_mask] = (
                #     wsi_tile_np[cell_mask] * (1 - params.alpha) + tile_img[cell_mask] * params.alpha
                # )

                vis_img = wsi_tile_overlaid

                wsi_tile_np = cv2.cvtColor(wsi_tile_np, cv2.COLOR_RGB2BGR)
                cv2.imshow("wsi_tile_np", wsi_tile_np)

                wsi_tile_overlaid = cv2.cvtColor(wsi_tile_overlaid, cv2.COLOR_RGB2BGR)
                cv2.imshow("wsi_tile_overlaid", wsi_tile_overlaid)

                tile_img = cv2.cvtColor(tile_img, cv2.COLOR_RGB2BGR)
                cv2.imshow("tile_img", tile_img)
            else:
                vis_img = tile_img

            # wsi_tile_vis = cv2.resize(wsi_tile_np, (tile_w_vis, tile_h_vis))

            tile_vis = cv2.resize(vis_img, (tile_w_vis, tile_h_vis))
            ox_vis = x // params.vis
            oy_vis = y // params.vis
            stitched_vis[oy_vis : oy_vis + tile_h_vis, ox_vis : ox_vis + tile_w_vis, ...] = tile_vis
            stitched_vis_ann = np.copy(stitched_vis)
            draw_box(stitched_vis_ann, [ox_vis, oy_vis, tile_w_vis, tile_h_vis])

            # print("showing image")
            cv2.imshow("stitched_vis", stitched_vis_ann)
            # print("done")
            k = cv2.waitKey(1 - pause)
            if k == 32:
                pause = 1 - pause
            if k == 27:
                exit(0)

    if params.save:
        # Flush once at the end, not after every tile
        if params.memmap:
            stitched.flush()

        output_path = os.path.join(params.output_dir, f"{prefix}.tif")
        print(f"Writing TIFF: {output_path}")

        tif_compression = None if params.compression == "none" else params.compression
        tifffile.imwrite(
            output_path,
            stitched,
            bigtiff=True,
            compression=tif_compression,
            photometric="rgb" if first_arr.ndim == 3 and channels >= 3 else None,
            metadata=None,
        )
        if params.memmap:
            del stitched
            try:
                os.remove(memmap_path)
            except OSError:
                pass

        print(f"Saved: {output_path}")


def main():

    params: Params = paramparse.process(Params)

    if params.gpu:
        try_init_cupy()
    else:
        print("GPU disabled via --gpu 0, using CPU.")

    print(f"WSI path: {params.wsi_path}")

    wsi = openslide.OpenSlide(params.wsi_path)

    params.tile_dir = linux_path(params.tile_dir)

    if params.tile_dir.endswith("/"):
        params.tile_dir = params.tile_dir[:-1]

    if not params.output_dir:
        params.output_dir = f"{params.tile_dir}-stitched"

    os.makedirs(params.output_dir, exist_ok=True)

    groups = collect_groups(params.tile_dir)

    if not groups:
        raise FileNotFoundError(
            f"No tile files matching the expected QuPath pattern were found in: {params.tile_dir}"
        )

    print(f"Found {len(groups)} prefix group(s):")
    for prefix in sorted(groups):
        print(f"  {prefix}: {len(groups[prefix])} tile(s)")

    if params.prefix:
        target = resolve_prefix(params.prefix, groups.keys())
        prefixes_to_run = [target]
        print(f"\nRestricting to prefix: {target!r}")
    else:
        prefixes_to_run = sorted(groups)

    for prefix in prefixes_to_run:
        stitch_group(prefix, groups[prefix], wsi, params)

    print("\nAll stitching complete.")


if __name__ == "__main__":
    main()
