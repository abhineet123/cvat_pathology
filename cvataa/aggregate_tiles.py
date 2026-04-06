import os
import re
import argparse
from collections import defaultdict

import numpy as np
from PIL import Image


FILENAME_RE = re.compile(
    r"^(?P<prefix>.+?)\s*\[x=(?P<x>-?\d+),y=(?P<y>-?\d+),w=(?P<w>\d+),h=(?P<h>\d+)\]\.(png|jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Aggregate small tiles into larger tiles.")
    parser.add_argument("--tile_dir", type=str, default=".")
    parser.add_argument("--output_dir", type=str, default="aggregated_tiles")
    parser.add_argument("--output_size", type=int, default=1024)
    return parser.parse_args()


def read_image(path):
    with Image.open(path) as img:
        return np.array(img)


def get_black(arr):
    val = 0.0
    if arr.ndim == 2:
        return val
    else:
        return np.array([val] * arr.shape[2], dtype=arr.dtype)


def get_white(arr):
    if np.issubdtype(arr.dtype, np.integer):
        val = np.iinfo(arr.dtype).max
    else:
        val = 1.0

    if arr.ndim == 2:
        return val
    else:
        return np.array([val] * arr.shape[2], dtype=arr.dtype)


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    groups = defaultdict(list)

    # -------------------------
    # Collect tiles
    # -------------------------
    for fname in os.listdir(args.tile_dir):
        m = FILENAME_RE.match(fname)
        if not m:
            continue

        prefix = m.group("prefix")
        x = int(m.group("x"))
        y = int(m.group("y"))

        groups[prefix].append(
            {"path": os.path.join(args.tile_dir, fname), "x": x, "y": y, "fname": fname}
        )

    # -------------------------
    # Process each prefix
    # -------------------------
    for prefix, tiles in groups.items():
        print(f"\nProcessing {prefix} ({len(tiles)} tiles)")

        # read first tile
        first = read_image(tiles[0]["path"])
        tile_h, tile_w = first.shape[:2]
        dtype = first.dtype

        black = get_black(first)

        big_tiles = {}

        # -------------------------
        # Assign tiles to big tiles
        # -------------------------
        for t in tiles:
            arr = read_image(t["path"])

            x, y = t["x"], t["y"]

            big_x = (x // args.output_size) * args.output_size
            big_y = (y // args.output_size) * args.output_size

            key = (big_x, big_y)

            if key not in big_tiles:
                if arr.ndim == 2:
                    big_tiles[key] = np.zeros((args.output_size, args.output_size), dtype=dtype)
                else:
                    big_tiles[key] = np.zeros(
                        (args.output_size, args.output_size, arr.shape[2]), dtype=dtype
                    )

            offset_x = x - big_x
            offset_y = y - big_y

            big_tiles[key][offset_y : offset_y + tile_h, offset_x : offset_x + tile_w] = arr

        # -------------------------
        # Save outputs
        # -------------------------
        for (bx, by), img in big_tiles.items():
            out_name = f"{prefix} [x={bx},y={by},w={args.output_size},h={args.output_size}].png"
            out_path = os.path.join(args.output_dir, out_name)

            Image.fromarray(img).save(out_path, format="PNG")

        print(f"Saved {len(big_tiles)} aggregated tiles for {prefix}")


if __name__ == "__main__":
    main()
