import os
import re
import math
import argparse
import cv2
from tqdm import tqdm
from collections import defaultdict

import numpy as np
from PIL import Image
import tifffile
import itertools
import paramparse

from cell_seg_utils import linux_path, draw_box

# Matches filenames like:
# D1 [x=70656,y=8704,w=512,h=512].png
# A1 [x=0,y=512,w=512,h=512].tif
FILENAME_RE = re.compile(
    r"^(?P<prefix>.+?)\s*\[x=(?P<x>-?\d+),y=(?P<y>-?\d+),w=(?P<w>\d+),h=(?P<h>\d+)\]\.(?P<ext>png|jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)


class Params(paramparse.CFG):
    """
    Stitch QuPath-exported tiles for every prefix in a folder into full-resolution TIFFs.
    :ivar compression: TIFF compression. Default: none
    :type compression: str

    :ivar output_dir: Folder to save stitched TIFF files. Default: {tile_dir}-stitched
    :type output_dir: str

    :ivar tile_dir: Folder containing tile images. Default: empty
    :type tile_dir: str

    :ivar vis: factor by which to resize the wsi for real-time visualization

    """

    def __init__(self):
        paramparse.CFG.__init__(self)

        self.compression = "none"
        self.output_dir = ""
        self.tile_dir = ""
        self.memmap = 1
        self.is_mask = 1
        self.vis = 0


def collect_groups(tile_dir):
    groups = defaultdict(list)

    for fname in os.listdir(tile_dir):
        if not os.path.isfile(linux_path(tile_dir, fname)):
            continue

        match = FILENAME_RE.match(fname)
        if not match:
            raise AssertionError(f"invalid fname: {fname}")

        prefix = match.group("prefix").strip()
        x = int(match.group("x"))
        y = int(match.group("y"))
        w = int(match.group("w"))
        h = int(match.group("h"))

        groups[prefix].append(
            {
                "fname": fname,
                "path": os.path.join(tile_dir, fname),
                "x": x,
                "y": y,
                "w_meta": w,
                "h_meta": h,
            }
        )

    for prefix in groups:
        groups[prefix] = sorted(groups[prefix], key=lambda t: (t["y"], t["x"], t["fname"]))

    return groups


def read_image(path):
    with Image.open(path) as img:
        return np.array(img), img.mode


def get_black_value(arr):
    black_scalar = 0.0

    if arr.ndim == 2:
        return black_scalar
    elif arr.ndim == 3:
        return np.array([black_scalar] * arr.shape[2], dtype=arr.dtype)
    else:
        raise ValueError(f"Unsupported array shape: {arr.shape}")


def get_white_value(arr):
    if np.issubdtype(arr.dtype, np.integer):
        white_scalar = np.iinfo(arr.dtype).max
    elif np.issubdtype(arr.dtype, np.floating):
        white_scalar = 1.0
    else:
        raise TypeError(f"Unsupported dtype: {arr.dtype}")

    if arr.ndim == 2:
        return white_scalar
    elif arr.ndim == 3:
        return np.array([white_scalar] * arr.shape[2], dtype=arr.dtype)
    else:
        raise ValueError(f"Unsupported array shape: {arr.shape}")


def apply_offset_to_mask(mask_rgb, max_cell_id, all_rgb_cols, rgb_cols_to_id):
    mask_rgb_flat = mask_rgb.reshape(-1, mask_rgb.shape[2])
    unique_rgb_vals = np.unique(mask_rgb_flat, axis=0)
    unique_rgb_vals = unique_rgb_vals.tolist()
    unique_rgb_vals.remove([0, 0, 0])

    unique_ids = list(rgb_cols_to_id[tuple(rgb_val)] for rgb_val in unique_rgb_vals)

    # assert 0 not in unique_ids, "0 should not be in unique_ids"
    # unique_ids.remove(0)

    offset_ids = [k + max_cell_id for k in unique_ids]

    mask_offset_flat = np.zeros_like(mask_rgb_flat)
    for rgb_val, offset_id in zip(unique_rgb_vals, offset_ids, strict=True):
        # https://stackoverflow.com/a/62642126
        mask_offset_flat[(mask_rgb_flat == rgb_val).all(axis=1)] = all_rgb_cols[offset_id]
    mask_offset = mask_offset_flat.reshape(mask_rgb.shape)

    # Image.fromarray(mask_offset).show("mask_offset")
    # Image.fromarray(mask_rgb).show("mask_rgb")

    # cv2.imshow("mask_rgb", mask_rgb)
    # cv2.imshow("mask_offset", mask_offset)
    # cv2.waitKey(0)

    if offset_ids:
        max_cell_id = max(offset_ids)

    return mask_offset, max_cell_id


def stitch_group(params: Params, prefix, tiles):
    print("\n" + "=" * 80)
    print(f"Processing prefix: {prefix}")
    print(f"Tiles found: {len(tiles)}")

    first_arr, first_mode = read_image(tiles[0]["path"])
    first_shape = first_arr.shape
    first_dtype = first_arr.dtype

    if first_arr.ndim == 2:
        tile_h, tile_w = first_arr.shape
        channels = None
    elif first_arr.ndim == 3:
        tile_h, tile_w, channels = first_arr.shape
    else:
        raise ValueError(f"Unsupported image shape for {tiles[0]['fname']}: {first_shape}")

    print(f"First tile: {tiles[0]['fname']}")
    print(f"Detected mode: {first_mode}")
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

    canvas_w = max_x - min_x
    canvas_h = max_y - min_y

    print(f"Output image size: {canvas_w} x {canvas_h}")

    if params.vis:
        vis_w = canvas_w // params.vis
        vis_h = canvas_h // params.vis

        tile_h_vis = tile_h // params.vis
        tile_w_vis = tile_w // params.vis

        print(f"vis image size: {vis_w} x {vis_h}")
        stitched_vis = np.zeros((vis_h, vis_w, 3), dtype=np.uint8)

    expected_cols = math.ceil(canvas_w / tile_w)
    expected_rows = math.ceil(canvas_h / tile_h)
    expected_slots = expected_cols * expected_rows
    missing_estimate = expected_slots - len(tiles)

    print(f"Estimated grid: {expected_cols} cols x {expected_rows} rows")
    if missing_estimate > 0:
        print(f"Estimated missing tile slots: {missing_estimate}")
        print("Missing regions will remain black.")

    output_path = os.path.join(params.output_dir, f"{prefix}.tif")

    stitched_shape = (canvas_h, canvas_w) if first_arr.ndim == 2 else (canvas_h, canvas_w, channels)

    if params.memmap:
        memmap_path = os.path.join(params.output_dir, f"{prefix}.memmap")
        stitched = np.memmap(
            memmap_path,
            dtype=first_dtype,
            mode="w+",
            shape=stitched_shape,
        )
        stitched[...] = get_black_value(first_arr)
    else:
        stitched = np.zeros_like(first_arr, shape=stitched_shape)

    # skipped = 0

    offset_id = 0

    all_rgb_cols = list(itertools.product(range(256), repeat=3))
    rgb_cols_to_id = {rgb_col: i for i, rgb_col in enumerate(all_rgb_cols)}

    pbar = tqdm(enumerate(tiles, start=1), total=len(tiles))

    for i, t in pbar:
        try:
            tile_img, _ = read_image(t["path"])
        except Exception as e:
            raise AssertionError(f"could not read {t['fname']}: {e}")
            # skipped += 1
            # continue

        if tile_img.shape != first_shape:
            raise AssertionError(f"invalid file {t['fname']} with shape mismatch: {tile_img.shape}")
            # skipped += 1
            # continue

        if params.is_mask:
            tile_img, offset_id = apply_offset_to_mask(
                tile_img, offset_id, all_rgb_cols, rgb_cols_to_id
            )

            pbar.set_description(f"n_objs: {offset_id}")

        ox = t["x"] - min_x
        oy = t["y"] - min_y
        stitched[oy : oy + tile_h, ox : ox + tile_w, ...] = tile_img
        # if i % 200 == 0 or i == len(tiles):
        # print(f"Pasted {i}/{len(tiles)} tiles")
        if params.vis:
            mask_offset_vis = cv2.resize(tile_img, (tile_h_vis, tile_w_vis))
            ox_vis = ox // params.vis
            oy_vis = oy // params.vis
            stitched_vis[oy_vis : oy_vis + tile_h_vis, ox_vis : ox_vis + tile_w_vis, ...] = (
                mask_offset_vis
            )
            stitched_vis_ann = np.copy(stitched_vis)
            draw_box(stitched_vis_ann, [ox_vis, oy_vis, tile_w_vis, tile_h_vis])
            cv2.imshow("stitched_vis", stitched_vis_ann)
            cv2.waitKey(1)

        if params.memmap:
            stitched.flush()

    tif_compression = None if params.compression == "none" else params.compression

    print(f"Writing TIFF: {output_path}")
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

    assert params.tile_dir, "tile_dir must be provided"
    params.tile_dir = linux_path(params.tile_dir)

    if params.tile_dir.endswith("/"):
        params.tile_dir = params.tile_dir[:-1]

    if not params.output_dir:
        params.output_dir = f"{params.tile_dir}-stiched"

    os.makedirs(params.output_dir, exist_ok=True)

    groups = collect_groups(params.tile_dir)

    if not groups:
        raise FileNotFoundError(
            f"No tile files matching the expected QuPath pattern were found in: {params.tile_dir}"
        )

    print(f"Found {len(groups)} prefix group(s):")
    for prefix in sorted(groups):
        print(f"  {prefix}: {len(groups[prefix])} tile(s)")

    for prefix in sorted(groups):
        stitch_group(params, prefix, groups[prefix])

    print("\nAll stitching complete.")


if __name__ == "__main__":
    main()
