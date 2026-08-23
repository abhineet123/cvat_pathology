import json
import numpy as np
import openslide
import tifffile
from tqdm import tqdm
from pathlib import Path
from shapely.geometry import shape, box, Polygon
from shapely.affinity import scale
import os
import cv2
from itertools import product

import paramparse

from cell_seg_utils import (
    Filter,
    linux_path,
    get_wsi_files,
    get_tiles_dirs,
)

from stitch_tiles import collect_groups


class Params(paramparse.CFG):
    def __init__(self):
        paramparse.CFG.__init__(self)
        self.filter = Filter()

        self.recursive = 0

        self.wsi_root_dir = "/data/PDL1-2026"
        self.wsi_dir = "NSCLC-B"
        self.wsi_exts = [
            ".svs",
        ]

        self.tiles_root_dir = "/data/PDL1-2026-Tiles"
        self.tiles_dir = "NSCLC-Tiles/256"

        # self.annotations_dir = "/data/PDL1-2026/NSCLC-B/annotations"

        self.start_id = 0
        self.end_id = -1

        self.internal_tile_size = 4096
        self.memmap = 0
        self.ds = 1.0
        self.load = 1
        self.area_threshold = 0
        self.skip_empty = 0
        self.vis = 0
        self.tiles = 0
        self.skip_interior_tiles = 1


def main():
    params: Params = paramparse.process(Params)

    if params.tiles == 2:
        params.skip_interior_tiles = 0

    wsi_files = get_wsi_files(
        params.wsi_root_dir, params.wsi_dir, params.wsi_exts, params.recursive, params.filter
    )
    n_wsi_files = len(wsi_files)

    wsi_out_dir = linux_path(params.wsi_root_dir, params.wsi_dir, "masks")
    os.makedirs(wsi_out_dir, exist_ok=True)

    if params.tiles:
        tiles_dirs = get_tiles_dirs(
            params.tiles_root_dir, params.tiles_dir, params.recursive, params.filter
        )
        n_tiles_dirs = len(tiles_dirs)
        assert (
            n_wsi_files == n_tiles_dirs
        ), f"mismatch between n_wsi_files ({n_wsi_files}) and n_tiles_dirs ({n_tiles_dirs})"
        tiles_out_dir = linux_path(params.tiles_root_dir, f"{params.tiles_dir}-masks")
        os.makedirs(tiles_out_dir, exist_ok=True)
    else:
        tiles_dirs = [
            None,
        ] * len(wsi_files)
        tiles_out_dir = None

    annotations_dir = linux_path(params.wsi_root_dir, params.wsi_dir, "annotations")
    assert os.path.exists(annotations_dir), f"nonexistent annotations_dir: {annotations_dir}"

    for wsi_id, (wsi_file, tiles_dir) in enumerate(zip(wsi_files, tiles_dirs, strict=True)):
        wsi_name = Path(wsi_file).stem
        if wsi_id < params.start_id:
            print(f"\nskipping WSI {wsi_id+1}/{n_wsi_files}: {wsi_name}\n")
            continue

        if wsi_id > params.end_id >= 0:
            print(f"\nskipping WSIs with id > {params.end_id}\n")
            break

        print(f"\n[{wsi_id + 1}/{n_wsi_files}] {wsi_name}")

        if params.tiles:
            tiles_name = Path(tiles_dir).name
            assert wsi_name in tiles_name, "mismatch between tiles_name and wsi_name"

        process_wsi(params, annotations_dir, wsi_file, wsi_out_dir, tiles_dir, tiles_out_dir)


def find_wsi_files(wsi_root: Path, wsi_exts: list) -> list:
    """
    Recursively find all WSI files under wsi_root,
    excluding _HE slides.
    """
    wsi_files = []
    for f in wsi_root.rglob("*"):
        if f.suffix.lower() not in wsi_exts:
            continue
        if "_HE" in f.stem:
            continue
        wsi_files.append(f)
    return sorted(wsi_files)


def find_annotation(annotations_dir: Path, wsi_stem: str) -> Path | None:
    """Find matching GeoJSON for a given WSI stem (e.g. 'E1' -> 'E1_annotations.geojson')."""
    candidate = annotations_dir / f"{wsi_stem}_annotations.geojson"
    return candidate if candidate.exists() else None


def load_annotations(geojson_path: Path, area_threshold, skip_empty):
    """Load all the annotation polygon from a QuPath GeoJSON export."""
    data = json.loads(geojson_path.read_text())
    features = data if isinstance(data, list) else data.get("features", [])

    non_overlapping_polygons = []

    if not features:
        msg = f"\nNo annotations found in GeoJSON file: {geojson_path}."
        if skip_empty:
            print("\n" + msg + "\n")
            return non_overlapping_polygons
        else:
            raise ValueError(msg)

    polygons = []
    for feat in features:
        try:
            if feat["properties"]["objectType"] != "annotation":
                continue
        except KeyError:
            pass

        geom = shape(feat["geometry"])

        if not geom.is_valid:
            geom = geom.buffer(0)

        polygons.append(geom)

    # largest = max(polygons, key=lambda g: g.area)
    # print(f"  Annotations : {len(polygons)} found — using largest (area = {largest.area:,.0f} px²)")

    filtered_polygons = [polygon for polygon in polygons if polygon.area > area_threshold]
    filtered_polygons.sort(key=lambda g: g.area, reverse=True)

    for polygon in filtered_polygons:
        if not any(fully_overlap(p, polygon) for p in non_overlapping_polygons):
            non_overlapping_polygons.append(polygon)

    print(
        f"loaded {len(polygons)} polygons out of which {len(non_overlapping_polygons)} are area_thresholded and non-overlapping"
    )
    return non_overlapping_polygons


def fully_overlap(p1: Polygon, p2: Polygon):
    non_intersecting = p1.difference(p1.intersection(p2))
    if non_intersecting.is_empty:
        return True
    return False


def burn_polygons_tiled(
    geoms, mask_w: int, mask_h: int, wsi_out_path, internal_tile_size, memmap, verbose=True
) -> np.ndarray:
    """
    Rasterize polygon into a mask tile-by-tile to keep RAM flat.
    Returns full uint8 mask (0 = background, 255 = tissue).
    """
    # For small masks (downsampled) just do it in one shot
    if mask_w * mask_h < 50_000_000:
        return burn_polygons_direct(geoms, mask_w, mask_h)

    # For large masks, tile the rasterization

    if memmap:
        assert wsi_out_path is not None, "wsi_out_path must be provided"
        memmap_path = Path(wsi_out_path) / "_tmp_mask.npy"
        # mask = np.lib.format.open_memmap(memmap_path, mode="w+", dtype=np.uint8, shape=(mask_h, mask_w))
        mask = np.memmap(memmap_path, mode="w+", dtype=np.uint8, shape=(mask_h, mask_w))
    else:
        mask = np.zeros(dtype=np.uint8, shape=(mask_h, mask_w))

    n_cols = int(np.ceil(mask_w / internal_tile_size))
    n_rows = int(np.ceil(mask_h / internal_tile_size))
    total = n_cols * n_rows
    # count = 0

    md_range = np.ndindex((n_rows, n_cols))
    # md_range = product(range(n_rows), range(n_cols))

    if verbose:
        pbar = tqdm(md_range, total=total)
    else:
        pbar = md_range

    non_zeros = 0

    for row, col in pbar:
        x = col * internal_tile_size
        y = row * internal_tile_size
        w = min(internal_tile_size, mask_w - x)
        h = min(internal_tile_size, mask_h - y)
        for geom in geoms:
            tile_mask = burn_tile(geom, x, y, w, h)
            if tile_mask is not None:
                mask[y : y + h, x : x + w][tile_mask] = 255
                # non_zeros += np.count_nonzero(tile_mask)
                # pbar.set_description(f"non_zeros: {non_zeros}")
        # count += 1
        # if count % 20 == 0 or count == total:
        #     print(f"    Tiling {count}/{total}...")

    if memmap:
        result = np.array(mask)
        del mask
        memmap_path.unlink(missing_ok=True)
    else:
        result = mask

    # total_non_zeros = np.count_nonzero(result)
    # print(f"total_non_zeros: {total_non_zeros}")

    return result


def burn_polygons_direct(geoms, mask_w: int, mask_h: int) -> np.ndarray:
    """Rasterize directly into a numpy array (for small/downsampled masks)."""
    mask = np.zeros((mask_h, mask_w), dtype=np.uint8)
    # parts = geoms.geoms if hasattr(geoms, "geoms") else [geoms]

    for poly in geoms:
        if poly.geom_type != "Polygon":
            continue
        coords = np.array(poly.exterior.coords, dtype=np.int32)
        cv2.fillPoly(mask, [coords], color=255)
        for interior in poly.interiors:
            hole = np.array(interior.coords, dtype=np.int32)
            cv2.fillPoly(mask, [hole], color=0)

    return mask


def burn_tile(geom, x: int, y: int, w: int, h: int) -> np.ndarray:
    """Rasterize polygon into a single tile."""
    tile_box = box(x, y, x + w, y + h)

    if not geom.intersects(tile_box):
        return None

    clipped = geom.intersection(tile_box)
    if clipped.is_empty:
        return None

    tile_mask = np.zeros((h, w), dtype=np.uint8)

    parts = clipped.geoms if hasattr(clipped, "geoms") else [clipped]
    for part in parts:
        if part.geom_type not in ("Polygon", "MultiPolygon"):
            continue
        sub_parts = part.geoms if part.geom_type == "MultiPolygon" else [part]
        for poly in sub_parts:
            coords = np.array(poly.exterior.coords, dtype=np.float32)
            coords[:, 0] -= x
            coords[:, 1] -= y
            cv2.fillPoly(tile_mask, [coords.astype(np.int32)], color=255)
            for interior in poly.interiors:
                hole = np.array(interior.coords, dtype=np.float32)
                hole[:, 0] -= x
                hole[:, 1] -= y
                cv2.fillPoly(tile_mask, [hole.astype(np.int32)], color=0)

    return tile_mask.astype(bool)


def process_wsi(
    params: Params,
    annotations_dir: str,
    wsi_path: str,
    wsi_out_dir: str,
    tiles_path: str,
    tiles_out_dir: str,
):
    vis_alpha = 0.18
    vis_color = np.asarray([0, 256, 0], dtype=np.float32)
    vis_size = 800

    wsi_path = Path(wsi_path)

    annotation_path = find_annotation(Path(annotations_dir), wsi_path.stem)
    assert annotation_path is not None, f"no annotation found for '{wsi_path.stem}'"

    print(f"reading annotations from {annotation_path}")

    wsi_out_name = wsi_path.stem
    if params.ds != 1.0:
        wsi_out_name = f"{wsi_out_name}_ds_{int(params.ds)}"
    wsi_out_path = linux_path(wsi_out_dir, wsi_out_name + ".tiff")

    slide = openslide.OpenSlide(wsi_path)
    wsi_w, wsi_h = slide.dimensions
    if params.vis:
        slide_vis = np.array(slide.get_thumbnail((vis_size, vis_size)))
    slide.close()

    factor = 1.0 / params.ds

    if params.load and os.path.exists(wsi_out_path):
        print(f"reading wsi mask from {wsi_out_path}")
        wsi_mask = tifffile.imread(wsi_out_path)
    else:

        mask_w = round(wsi_w / params.ds)
        mask_h = round(wsi_h / params.ds)

        print(f"WSI size: {wsi_w} x {wsi_h}")
        print(f"Mask size: {mask_w} x {mask_h}  (downsample={params.ds})")

        geoms = load_annotations(
            annotation_path, params.area_threshold, skip_empty=params.skip_empty
        )
        if not geoms:
            return

        if params.ds != 1.0:
            geoms = [scale(geom, xfact=factor, yfact=factor, origin=(0, 0)) for geom in geoms]

        print(f"  Rasterizing...")
        wsi_mask = burn_polygons_tiled(
            geoms,
            mask_w,
            mask_h,
            wsi_out_dir,
            params.internal_tile_size,
            params.memmap,
        )

        print(f"Writing WSI mask to {wsi_out_path}")
        tifffile.imwrite(
            wsi_out_path,
            wsi_mask,
            bigtiff=True,
            tile=(512, 512),
            photometric="minisblack",
            compression="zstd",
            compressionargs={"level": 1},
        )
    if params.vis:
        slide_vis_h, slide_vis_w = slide_vis.shape[:2]
        wsi_mask_vis = cv2.resize(
            wsi_mask,
            (slide_vis_w, slide_vis_h),
            # interpolation=cv2.INTER_NEAREST_EXACT,
            interpolation=cv2.INTER_LINEAR,
        )

        # non_zeros = np.count_nonzero(wsi_mask)
        # print(f"non_zeros: {non_zeros}")

        vis_non_zeros = np.count_nonzero(wsi_mask_vis)
        print(f"vis_non_zeros: {vis_non_zeros}")

        wsi_mask_b = wsi_mask_vis.astype(bool)
        slide_vis[wsi_mask_b] = (
            slide_vis[wsi_mask_b].astype(np.float32) * (1 - vis_alpha) + vis_color * vis_alpha
        )
        if params.vis == 2:
            wsi_vis_out_dir = wsi_out_dir + "-vis"
            os.makedirs(wsi_vis_out_dir, exist_ok=1)
            wsi_vis_out_path = linux_path(wsi_vis_out_dir, wsi_out_name + ".png")
            print(f"Writing WSI vis to {wsi_vis_out_path}")
            cv2.imwrite(wsi_vis_out_path, slide_vis)
        else:
            cv2.imshow("slide_vis", slide_vis)
            cv2.imshow("wsi mask", wsi_mask_vis)
            # cv2.waitKey(0)

    if not params.tiles:
        return

    groups = collect_groups(tiles_path)
    if not groups:
        raise FileNotFoundError(
            f"No tile files matching the expected QuPath pattern were found in: {tiles_path}"
        )
    assert len(groups) == 1, "multiple prefix groups found"

    # xs, ys = zip(*[(tile_info["x"], tile_info["y"]) for tile_info in tiles_info])
    # roi_min_x, roi_max_x = np.amin(xs), np.amax(xs)
    # roi_min_y, roi_max_y = np.amin(ys), np.amax(ys)
    # roi_w, roi_h = roi_max_x - roi_min_x, roi_max_y - roi_min_y
    tiles_info = next(iter(groups.values()), None)
    n_tiles = len(tiles_info)

    tiles_out_path = linux_path(tiles_out_dir, Path(tiles_path).stem)
    os.makedirs(tiles_out_path, exist_ok=True)

    if params.vis == 2:
        tiles_vis_out_path = linux_path(tiles_out_dir + "-vis", Path(tiles_path).stem)
        os.makedirs(tiles_vis_out_path, exist_ok=True)
        print(f"saving vis tile images to {tiles_vis_out_path}")

    print(f"writing tile masks to {tiles_out_path}")

    for tile_info in tqdm(tiles_info, total=n_tiles):
        x, y = tile_info["x"], tile_info["y"]
        tile_w, tile_h = tile_info["w_meta"], tile_info["h_meta"]

        if params.ds != 1.0:
            x, y = int(x * factor), int(y * factor)
            tile_w, tile_h = int(tile_w * factor), int(tile_h * factor)

        tile_fname = tile_info["fname"]

        tile_path = linux_path(tiles_path, tile_fname)
        tile_img = cv2.imread(tile_path)

        tile_img_h, tile_img_w = tile_img.shape[:2]

        tile_mask = wsi_mask[y : y + tile_h, x : x + tile_w]
        # tile_mask = mask.read_region(location=(x, y), level=0, size=(tile_w, tile_h))

        if params.skip_interior_tiles:
            n_zeros = tile_mask.size - np.count_nonzero(tile_mask)
            if not n_zeros:
                continue

        if params.ds != 1.0:
            tile_mask = cv2.resize(
                tile_mask,
                (tile_img_w, tile_img_h),
                interpolation=cv2.INTER_NEAREST_EXACT,
                # interpolation=cv2.INTER_LINEAR,
            )

        if params.vis:
            tile_mask_b = tile_mask.astype(bool)
            tile_img[tile_mask_b] = (
                tile_img[tile_mask_b].astype(np.float32) * (1 - vis_alpha) + vis_color * vis_alpha
            )
            if params.vis == 2:
                tile_vis_mask_path = linux_path(tiles_vis_out_path, tile_fname)
                cv2.imwrite(tile_vis_mask_path, tile_img)
            else:
                cv2.imshow("tile_img", tile_img)
                cv2.imshow("tile_mask", tile_mask)
                k = cv2.waitKey(0)
                if k == 27:
                    exit(0)

        tile_mask_path = linux_path(tiles_out_path, tile_fname)
        cv2.imwrite(tile_mask_path, tile_mask)


if __name__ == "__main__":
    main()
