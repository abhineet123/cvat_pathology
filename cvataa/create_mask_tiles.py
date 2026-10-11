import os
import re
import paramparse
import cv2
import tifffile
import itertools
from tqdm import tqdm
from PIL import Image
import numpy as np

Image.MAX_IMAGE_PIXELS = None

FILENAME_RE = re.compile(
    r"^(?P<prefix>.+?)\s*\[x=(?P<x>-?\d+),y=(?P<y>-?\d+),w=(?P<w>\d+),h=(?P<h>\d+)\]\.(?P<ext>png|jpg|jpeg|tif|tiff)$",
    re.IGNORECASE,
)
from cell_seg_utils import linux_path, overlay_cells, remove_offset_from_mask


def parse_tile_name(fname):
    m = FILENAME_RE.match(fname)
    if not m:
        return None

    return {
        "prefix": m.group("prefix").strip(),
        "x": int(m.group("x")),
        "y": int(m.group("y")),
        "w": int(m.group("w")),
        "h": int(m.group("h")),
    }


class Params:
    """
    :ivar full_mask_path:
    :type full_mask_path: str

    :ivar output_dir:
    :type output_dir: str

    :ivar output_ext:
    :type output_ext: str

    :ivar source_256_dir:
    :type source_256_dir: str

    """

    def __init__(self):
        self.cfg = ()
        self.root_dir = ""
        self.mask_path = ""
        self.output_dir = ""
        self.output_ext = "png"
        self.source_dir = ""
        self.source_ext = "png"

        self.alpha = 0.5
        self.vis = 0


def main():
    params: Params = paramparse.process(Params)

    all_rgb_cols = list(itertools.product(range(256), repeat=3))

    if params.root_dir:
        params.mask_path = linux_path(params.root_dir, params.mask_path)
        params.output_dir = linux_path(params.root_dir, params.output_dir)

    os.makedirs(params.output_dir, exist_ok=True)

    print(f"Loading full WSI mask: {params.mask_path}")
    full_mask = tifffile.imread(params.mask_path)

    H, W = full_mask.shape[:2]
    print(f"Full mask size: {W} x {H}")

    source_tiles = sorted(
        k for k in os.listdir(params.source_dir) if k.endswith(f".{params.source_ext}")
    )

    pause = 1

    for source_tile_name in tqdm(source_tiles):
        info = parse_tile_name(source_tile_name)

        if info is None:
            raise AssertionError(f"invalid source tile: {source_tile_name}")

        x = info["x"]
        y = info["y"]
        w = info["w"]
        h = info["h"]

        if x < 0 or y < 0 or x + w > W or y + h > H:
            raise AssertionError(f"out of bounds source tile: {source_tile_name}")

        tile_mask = full_mask[y : y + h, x : x + w, ...]

        tile_mask = remove_offset_from_mask(tile_mask, all_rgb_cols)
        out_name = f'{info["prefix"]} [x={x},y={y},w={w},h={h}].{params.output_ext}'
        out_path = os.path.join(params.output_dir, out_name)

        if params.vis:
            source_tile_path = linux_path(params.source_dir, source_tile_name)

            source_tile = np.array(Image.open(source_tile_path))
            source_tile_overlaid = overlay_cells(source_tile, tile_mask, params.alpha)

            source_tile = cv2.cvtColor(source_tile, cv2.COLOR_RGB2BGR)
            cv2.imshow("source_tile", source_tile)

            source_tile_overlaid = cv2.cvtColor(source_tile_overlaid, cv2.COLOR_RGB2BGR)
            cv2.imshow("source_tile_overlaid", source_tile_overlaid)

            tile_mask = cv2.cvtColor(tile_mask, cv2.COLOR_RGB2BGR)
            cv2.imshow("tile_mask", tile_mask)

            k = cv2.waitKey(1 - pause)
            if k == 32:
                pause = 1 - pause
            if k == 27:
                exit(0)

        Image.fromarray(tile_mask).save(out_path)


if __name__ == "__main__":
    main()
