import os
import re
import argparse
import csv

import numpy as np
from PIL import Image

import paramparse

from cell_seg_utils import linux_path, draw_box

Image.MAX_IMAGE_PIXELS = None

FILENAME_RE = re.compile(
    r"^(?P<prefix>.+?)\s*\[x=(?P<x>-?\d+),y=(?P<y>-?\d+),w=(?P<w>\d+),h=(?P<h>\d+)\]\.(?P<ext>png|jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)


class Params(paramparse.CFG):
    """
    Crop mask tiles from a stitched WSI mask using CSV metadata.

    :ivar mask_path: Path to the stitched WSI mask image.
    :type mask_path: str

    :ivar metadata_csv: Path to the tile metadata CSV. Defaults to {mask_name}_tile_metadata.csv in the same folder as the mask
    :type metadata_csv: str

    :ivar output_dir: Directory to save output mask tiles.
    :type output_dir: str

    :ivar output_ext: Output extension for generated mask tiles.
    :type output_ext: str

    :ivar pad_mode: How to handle crops that go outside the stitched mask bounds.
    :type pad_mode: str

    :ivar tile_size: Output tile size in pixels (e.g. 256, 512, 1024)
    :type tile_size: int

    :ivar stride: Stride between tiles in pixels. Defaults to --tile_size (no overlap).
    :type stride: int

    """

    def __init__(self):
        paramparse.CFG.__init__(self)

        self.root_dir = ""
        self.mask_path = None
        self.metadata_csv = None
        self.output_dir = None
        self.output_ext = "png"
        self.pad_mode = "black"
        self.tile_size = None
        self.stride = None


def resolve_metadata_path(mask_path, metadata_csv):
    """
    If metadata_csv is not provided, look for {mask_stem}_tile_metadata.csv
    in the same directory as the mask.
    """
    if metadata_csv:
        return metadata_csv

    mask_dir = os.path.dirname(os.path.abspath(mask_path))
    mask_stem = os.path.splitext(os.path.basename(mask_path))[0]
    candidate = os.path.join(mask_dir, f"{mask_stem}_tile_metadata.csv")

    if not os.path.isfile(candidate):
        raise FileNotFoundError(
            f"Could not find metadata CSV at: {candidate}\n"
            f"Please provide --metadata_csv explicitly."
        )

    print(f"Using metadata CSV: {candidate}")
    return candidate


def load_metadata(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "fname": row["fname"],
                    "path": row["path"],
                    "x": int(row["x"]),
                    "y": int(row["y"]),
                    "w_meta": int(row["w_meta"]),
                    "h_meta": int(row["h_meta"]),
                    "actual_w": int(row["actual_w"]),
                    "actual_h": int(row["actual_h"]),
                    "canvas_w": int(row["canvas_w"]),
                    "canvas_h": int(row["canvas_h"]),
                    "min_x": int(row["min_x"]),
                    "min_y": int(row["min_y"]),
                }
            )
    return rows


def read_image(path):
    with Image.open(path) as img:
        return np.array(img)


def crop_tile(arr, x, y, w, h):
    """Crop a tile from arr at (x, y) with size (w, h). Returns None if out of bounds."""
    H, W = arr.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return None
    return arr[y : y + h, x : x + w]


def is_blank(tile):
    """Returns True if the tile contains no non-zero pixels."""
    return not np.any(tile)


def generate_tile_positions(canvas_w, canvas_h, min_x, min_y, tile_size, stride):
    """
    Generate all (x, y) top-left positions for tiles of `tile_size` across the canvas,
    using `stride` step. Positions are in original WSI coordinates.
    """
    positions = []
    y = min_y
    while y + tile_size <= min_y + canvas_h:
        x = min_x
        while x + tile_size <= min_x + canvas_w:
            positions.append((x, y))
            x += stride
        y += stride
    return positions


def main():
    params: Params = paramparse.process(Params)

    if params.root_dir:
        params.mask_path = linux_path(params.root_dir, params.mask_path)
        params.output_dir = linux_path(params.root_dir, params.output_dir)

    stride = params.stride if params.stride is not None else params.tile_size
    os.makedirs(params.output_dir, exist_ok=True)

    metadata_csv = resolve_metadata_path(params.mask_path, params.metadata_csv)
    metadata = load_metadata(metadata_csv)

    if not metadata:
        raise ValueError(f"No rows found in metadata CSV: {metadata_csv}")

    # All rows share the same canvas/origin info — read from first row
    first = metadata[0]
    canvas_w = first["canvas_w"]
    canvas_h = first["canvas_h"]
    min_x = first["min_x"]
    min_y = first["min_y"]

    # Derive prefix from first fname
    m = FILENAME_RE.match(first["fname"])
    prefix = m.group("prefix").strip() if m else "tile"

    print(f"Loading mask: {params.mask_path}")
    mask = read_image(params.mask_path)
    print(f"Mask shape: {mask.shape}")
    print(f"Canvas size from metadata: {canvas_w} x {canvas_h}")
    print(f"Canvas origin: ({min_x}, {min_y})")
    print(f"Tile size: {params.tile_size}  Stride: {stride}")

    mask_h, mask_w = mask.shape[:2]
    if mask_h != canvas_h or mask_w != canvas_w:
        print(
            f"Warning: mask shape ({mask_w}x{mask_h}) does not match "
            f"canvas size ({canvas_w}x{canvas_h}). Cropping may be inaccurate."
        )

    positions = generate_tile_positions(canvas_w, canvas_h, min_x, min_y, params.tile_size, stride)
    print(f"Total tile positions to crop: {len(positions)}")
    print("Blank (all-black) tiles will be skipped — positions are recoverable from the CSV.")

    processed = 0
    skipped_blank = 0
    skipped_bounds = 0
    failed = 0

    for wx, wy in positions:
        # Convert WSI coordinates to mask-local coordinates
        lx = wx - min_x
        ly = wy - min_y

        tile = crop_tile(mask, lx, ly, params.tile_size, params.tile_size)
        if tile is None:
            skipped_bounds += 1
            continue

        if is_blank(tile):
            skipped_blank += 1
            continue

        out_name = f"{prefix} [x={wx},y={wy},w={params.tile_size},h={params.tile_size}].{params.output_ext}"
        out_path = os.path.join(params.output_dir, out_name)

        try:
            Image.fromarray(tile).save(out_path)
            processed += 1
        except Exception as e:
            print(f"Failed to save {out_name}: {e}")
            failed += 1

    print("\nDone.")
    print(f"Processed:      {processed}")
    print(f"Skipped blank:  {skipped_blank}")
    print(f"Skipped bounds: {skipped_bounds}")
    print(f"Failed:         {failed}")


if __name__ == "__main__":
    main()
