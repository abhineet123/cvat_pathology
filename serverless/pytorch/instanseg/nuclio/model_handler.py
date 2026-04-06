# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import numpy as np
import torch
from instanseg import InstanSeg
from skimage.measure import approximate_polygon, find_contours


def to_contour(mask):
    # mask.shape
    contours = find_contours(mask)
    contour = contours[0]
    contour = np.flip(contour, axis=1)
    contour = approximate_polygon(contour, tolerance=2.5)

    return contour


def to_cvat_mask(box: list, mask):
    xtl, ytl, xbr, ybr = box
    flattened = mask[ytl : ybr + 1, xtl : xbr + 1].flat[:].tolist()

    flattened = list(map(int, flattened))
    flattened.extend([xtl, ytl, xbr, ybr])
    return flattened


class ModelHandler:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.latest_image = None
        self.predictor = InstanSeg("brightfield_nuclei", verbosity=0, device=self.device)

    def infer(self, image, context, threshold):
        pixel_size = None
        labeled_output = self.predictor.eval_small_image(
            np.array(image), pixel_size, return_image_tensor=False
        )

        labeled_output_np = labeled_output.cpu().detach().numpy().squeeze().astype(np.int64)
        cell_ids = np.unique(labeled_output_np)
        obj_type = "mask"
        obj_label = "nucleus"

        results = []

        # exclude cell_id 0
        n_cells = len(cell_ids) - 1

        for i, cell_id in enumerate(cell_ids):
            if cell_id == 0:
                continue
            cell_mask = labeled_output_np == cell_id
            ys, xs = np.nonzero(cell_mask)
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
            bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

            context.logger.info(f"{obj_label} {i} / {n_cells}: {bbox}")

            result = {
                "confidence": str(1),
                "label": obj_label,
                "type": obj_type,
            }
            cell_mask_uint8 = cell_mask.astype(np.uint8) * 255
            cvat_mask = to_cvat_mask(bbox, cell_mask_uint8)
            contour = to_contour(cell_mask_uint8)
            result.update(
                {
                    "points": contour.ravel().tolist(),
                    "mask": cvat_mask,
                }
            )
            results.append(result)
        return results
