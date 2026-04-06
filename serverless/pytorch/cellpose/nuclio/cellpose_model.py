# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import numpy as np
import torch
from skimage.measure import approximate_polygon, find_contours

from cellpose import models as cellpose_models


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


class CellPoseModel:
    def __init__(self):
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        pretrained_model = "cpsam"
        # pixel_size = 0.2632
        # cell_size = 200
        # self.diameter = cell_size / pixel_size
        self.predictor = cellpose_models.CellposeModel(
            device=self.device,
            pretrained_model=pretrained_model,
        )

    def infer(self, image, context, threshold):

        image_np = np.array(image)
        flow_threshold = 0
        tile_norm_blocksize = 0
        cellprob_threshold = -10 * threshold

        context.logger.info(f"cellprob_threshold: {cellprob_threshold}")

        out = self.predictor.eval(
            image_np,
            niter=1000,
            # diameter=self.diameter,
            diameter=None,
            normalize={"tile_norm_blocksize": tile_norm_blocksize},
            do_3D=False,
            augment=False,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
            stitch_threshold=0.0,
            min_size=-1,
            batch_size=64,
            bsize=256,
            resample=True,
            channel_axis=None,
            z_axis=None,
            flow3D_smooth=0,
        )
        masks, flows = out[:2]
        # cellprob = flows[-1]

        results = []

        cell_ids = np.unique(masks)

        # exclude cell_id 0
        n_cells = len(cell_ids) - 1

        for i, cell_id in enumerate(cell_ids):
            if cell_id == 0:
                continue
            cell_mask = masks == cell_id
            ys, xs = np.nonzero(cell_mask)
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
            bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

            context.logger.info(f"{i} / {n_cells}: {bbox}")

            cell_mask_uint8 = cell_mask.astype(np.uint8) * 255
            cvat_mask = to_cvat_mask(bbox, cell_mask_uint8)
            contour = to_contour(cell_mask_uint8)

            result = {
                "confidence": str(1),
                "label": "nucleus",
                "type": "mask",
                "points": contour.ravel().tolist(),
                "mask": cvat_mask,
            }

            results.append(result)
        return results
