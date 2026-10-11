import os
import re
import argparse

import numpy as np
from PIL import Image


FILENAME_RE = re.compile(
    r'^(?P<prefix>.+?)\s*\[x=(?P<x>-?\d+),y=(?P<y>-?\d+),w=(?P<w>\d+),h=(?P<h>\d+)\]\.(png|jpg|jpeg|tif|tiff)$',
    re.IGNORECASE
)


def parse_args():
    parser = argparse.ArgumentParser(description="Retile reconstructed images/masks into smaller tiles.")
    parser.add_argument("--tile_dir", type=str, required=True,
                        help="Directory containing reconstructed large images/masks.")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Directory to save smaller retiled outputs.")
    parser.add_argument("--output_size", type=int, default=512,
                        help="Output tile size, e.g. 512.")
    parser.add_argument("--pad_mode", type=str, choices=["black", "white", "skip"], default="black",
                        help="How to handle edge tiles smaller than tile_size.")
    return parser.parse_args()


def read_image(path):
    with Image.open(path) as img:
        return np.array(img)


def get_fill_value(arr, mode):
    if mode == "black":
        if arr.ndim == 2:
            return 0
        return np.zeros(arr.shape[2], dtype=arr.dtype)

    if mode == "white":
        if np.issubdtype(arr.dtype, np.integer):
            val = np.iinfo(arr.dtype).max
        else:
            val = 1.0

        if arr.ndim == 2:
            return val
        return np.array([val] * arr.shape[2], dtype=arr.dtype)

    return None  # for skip


def pad_tile(tile, tile_size, fill_value):
    h, w = tile.shape[:2]

    if tile.ndim == 2:
        out = np.full((tile_size, tile_size), fill_value, dtype=tile.dtype)
    else:
        out = np.full((tile_size, tile_size, tile.shape[2]), fill_value, dtype=tile.dtype)

    out[:h, :w] = tile
    return out


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    valid_exts = (".png", ".jpg", ".jpeg", ".tif", ".tiff")

    for fname in os.listdir(args.tile_dir):
        if not fname.lower().endswith(valid_exts):
            continue

        m = FILENAME_RE.match(fname)
        if not m:
            print(f"Skipping file with unexpected name format: {fname}")
            continue

        prefix = m.group("prefix")
        base_x = int(m.group("x"))
        base_y = int(m.group("y"))

        in_path = os.path.join(args.tile_dir, fname)
        arr = read_image(in_path)

        H, W = arr.shape[:2]
        tile_size = args.output_size
        fill_value = get_fill_value(arr, args.pad_mode)

        saved = 0

        for y0 in range(0, H, tile_size):
            for x0 in range(0, W, tile_size):
                tile = arr[y0:y0 + tile_size, x0:x0 + tile_size]
                h, w = tile.shape[:2]

                if h < tile_size or w < tile_size:
                    if args.pad_mode == "skip":
                        continue
                    tile = pad_tile(tile, tile_size, fill_value)

                out_x = base_x + x0
                out_y = base_y + y0

                out_name = f"{prefix} [x={out_x},y={out_y},w={tile_size},h={tile_size}].png"
                out_path = os.path.join(args.output_dir, out_name)

                Image.fromarray(tile).save(out_path, format="PNG")
                saved += 1

        print(f"Processed {fname} -> saved {saved} tiles")


if __name__ == "__main__":
    main()