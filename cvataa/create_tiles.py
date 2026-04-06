import os
import re
import argparse

import numpy as np
from PIL import Image

import paramparse

from cell_seg_utils import linux_path, draw_box


FILENAME_RE = re.compile(
    r"^(?P<prefix>.+?)\s*\[x=(?P<x>-?\d+),y=(?P<y>-?\d+),w=(?P<w>\d+),h=(?P<h>\d+)\]\.(?P<ext>png|jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)


class Params(paramparse.CFG):
    """
    Create mask tiles from a stitched WSI mask using a reference tile directory.
    :ivar mask_path: Path to the stitched WSI mask image.
    :type mask_path: str

    :ivar output_dir: Directory to save output mask tiles.
    :type output_dir: str

    :ivar output_ext: Output extension for generated mask tiles.
    :type output_ext: str

    :ivar pad_mode: How to handle crops that go outside the stitched mask bounds.
    :type pad_mode: str

    :ivar reference_dir: Directory containing the original reference tiles whose filenames define crop regions.
    :type reference_dir: str

    :ivar tile_size: Optional expected tile size for validation.
    :type tile_size: int

    """

    def __init__(self):
        paramparse.CFG.__init__(self)

        self.root_dir = ""
        self.mask_path = None
        self.output_dir = None
        self.output_ext = "png"
        self.pad_mode = "black"
        self.reference_dir = None
        self.tile_size = None


def read_image(path):
    with Image.open(path) as img:
        return np.array(img)


def get_black_fill(arr):
    if arr.ndim == 2:
        return 0
    return np.zeros(arr.shape[2], dtype=arr.dtype)


def crop_with_padding(arr, x, y, w, h, pad_mode="black"):
    H, W = arr.shape[:2]

    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(W, x + w)
    y2 = min(H, y + h)

    if x1 >= x2 or y1 >= y2:
        if pad_mode == "skip":
            return None
        if arr.ndim == 2:
            out = np.zeros((h, w), dtype=arr.dtype)
        else:
            out = np.zeros((h, w, arr.shape[2]), dtype=arr.dtype)
        return out

    crop = arr[y1:y2, x1:x2]

    if crop.shape[0] == h and crop.shape[1] == w:
        return crop

    if pad_mode == "skip":
        return None

    fill = get_black_fill(arr)
    if arr.ndim == 2:
        out = np.full((h, w), fill, dtype=arr.dtype)
    else:
        out = np.full((h, w, arr.shape[2]), fill, dtype=arr.dtype)

    out_y1 = y1 - y
    out_x1 = x1 - x
    out[out_y1 : out_y1 + crop.shape[0], out_x1 : out_x1 + crop.shape[1]] = crop
    return out


def main():
    params: Params = paramparse.process(Params)

    assert params.mask_path is not None, "mask_path must be provided"
    assert params.reference_dir is not None, "reference_dir must be provided"

    if params.root_dir:
        params.mask_path = linux_path(params.root_dir, params.mask_path)

    os.makedirs(params.output_dir, exist_ok=True)

    mask = read_image(params.mask_path)
    H, W = mask.shape[:2]

    print(f"Loaded mask: {params.mask_path}")
    print(f"Mask shape: {mask.shape}")
    print(f"Reference dir: {params.reference_dir}")
    print(f"Output dir: {params.output_dir}")

    ref_files = sorted(os.listdir(params.reference_dir))

    processed = 0
    skipped = 0
    failed = 0

    for fname in ref_files:
        ref_path = os.path.join(params.reference_dir, fname)
        if not os.path.isfile(ref_path):
            continue

        m = FILENAME_RE.match(fname)
        if not m:
            print(f"Skipping filename with unexpected format: {fname}")
            skipped += 1
            continue

        prefix = m.group("prefix")
        x = int(m.group("x"))
        y = int(m.group("y"))
        w = int(m.group("w"))
        h = int(m.group("h"))

        if params.tile_size is not None:
            if w != params.tile_size or h != params.tile_size:
                print(
                    f"Skipping {fname}: filename tile size ({w}x{h}) "
                    f"does not match expected --tile_size {params.tile_size}"
                )
                skipped += 1
                continue

        tile = crop_with_padding(mask, x, y, w, h, pad_mode=params.pad_mode)
        if tile is None:
            print(f"Skipping {fname}: crop outside bounds and pad_mode=skip")
            skipped += 1
            continue

        out_name = f"{prefix} [x={x},y={y},w={w},h={h}].{params.output_ext}"
        out_path = os.path.join(params.output_dir, out_name)

        try:
            Image.fromarray(tile).save(out_path)
            processed += 1
        except Exception as e:
            print(f"Failed to save {out_name}: {e}")
            failed += 1

    print("\nDone.")
    print(f"Processed: {processed}")
    print(f"Skipped:   {skipped}")
    print(f"Failed:    {failed}")


if __name__ == "__main__":
    main()
