import cv2
import uuid

import numpy as np
from tqdm import tqdm

from cell_seg_params import CellSegParams

from cell_seg_utils import (
    draw_box,
    resize_ar,
)


class CellSegWSIBase:
    def __init__(self, name, file_mode, params: CellSegParams):
        self.name = name
        self.params: CellSegParams = params
        self.file_mode = file_mode
        self.frame_id = 0
        self.label_map = {0: "nucleus"}

    def show(self, tile_cells, tile_img_np):
        n_tile_cells = len(tile_cells)
        if n_tile_cells == 0:
            return
        tile_img_vis = cv2.cvtColor(tile_img_np, cv2.COLOR_RGB2BGR)
        print(f"drawing {n_tile_cells} cells")
        for tile_cell in tile_cells:
            class_id = tile_cell["type"]
            # if class_id == 0:
            # continue
            class_name = self.label_map[class_id]
            draw_box(
                tile_img_vis,
                box=tile_cell["bbox"],
                mask=tile_cell["mask"],
                xywh=False,
                alpha=0.25,
                _id=class_name,
                color=self.params.cols[class_id],
            )
        tile_img_vis = resize_ar(tile_img_vis, max=600)
        cv2.imshow("tile_img_vis", tile_img_vis)
        k = cv2.waitKey(0)
        if k == 27:
            exit(0)

    def detect(self, wsi):
        raise NotImplementedError

    def detect_in_file(self, wsi_path, mask_path, ann_path, outdir):
        raise NotImplementedError

    @staticmethod
    def instance_mask_to_cells(
        instance_mask: np.ndarray,
        tile_offset,
    ):
        # Source - https://stackoverflow.com/a/30003565
        # Posted by gg349, modified by community. See post 'Timeline' for change history
        # Retrieved 2026-05-17, License - CC BY-SA 4.0

        # creates an array of indices, sorted by unique element
        instance_mask_flat = instance_mask.flatten()
        idx_sort = np.argsort(instance_mask_flat, axis=None, kind="mergesort")

        # sorts records array so all unique elements are together
        sorted_instance_mask = instance_mask_flat[idx_sort]

        # returns the unique values, the index of the first occurrence of a value, and the count for each element
        vals, idx_start = np.unique(sorted_instance_mask, return_index=True)

        # splits the indices into separate arrays
        res1d = np.split(idx_sort, idx_start[1:])
        res2d = [np.unravel_index(k, instance_mask.shape) for k in res1d]

        results = []

        tile_x, tile_y = tile_offset

        pbar = zip(vals, res2d, strict=True)
        # pbar = tqdm(
        #     pbar,
        #     desc="extracting cells from instance mask",
        #     total=len(vals),
        # )
        for cell_id, coords in pbar:
            if cell_id == 0:
                continue

            ys, xs = coords
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)

            if xmax <= xmin or ymax <= ymin:
                continue

            cell_bbox_tile = [int(xmin), int(ymin), int(xmax), int(ymax)]
            cell_bbox_wsi = [
                int(xmin + tile_x),
                int(ymin + tile_y),
                int(xmax + tile_x),
                int(ymax + tile_y),
            ]

            cell_mask = instance_mask[ymin:ymax, xmin:xmax]

            cell_mask_bin = cell_mask == cell_id

            cell_area = np.count_nonzero(cell_mask_bin)

            # cell_mask_uint8 = cell_mask.astype(np.uint8) * 255
            # contour_cv = to_contour_cv(cell_mask_uint8)
            # contour = to_contour(cell_mask_uint8).ravel().tolist()

            result_raw = {
                "type": 0,
                # "id": str(uuid.uuid4()),
                "id": f"{tile_x}_{tile_y}-{cell_id}",
                "mask": cell_mask_bin,
                "tile_bbox": cell_bbox_tile,
                "wsi_bbox": cell_bbox_wsi,
                "area": cell_area,
                "to_delete": 0,
                "ioa": {},
            }

            results.append(result_raw)

        return results
