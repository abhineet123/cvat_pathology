import numpy as np
import base64
import io
import cv2
import torch
from skimage.measure import approximate_polygon, find_contours
from PIL import Image

from cellpose import models as cellpose_models


def to_contour(mask):
    # mask.shape
    contours = find_contours(mask)
    contour = contours[0]
    contour = np.flip(contour, axis=1)
    contour = approximate_polygon(contour, tolerance=2.5)

    return contour


def point_is_in_box(pt: list, box: list):
    x, y = pt
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


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
        self.prev_image = None
        self.prev_mask = None

        self.prev_roi = None
        self.prev_roi_masks = []
        self.prev_roi_bboxes = []

    def infer_with_roi(self, event, context, threshold, roi, pos_points):

        image_bytes = event.body["image"]
        repeat_image = self.prev_image == image_bytes

        context.logger.info(f"\nrepeat_image: {repeat_image}")

        context.logger.info(f"pos_points: {pos_points}")
        context.logger.info(f"roi: {roi}")
        context.logger.info(f"self.prev_roi : {self.prev_roi }")

        auto_roi = False
        if not repeat_image:
            # first call on this image without roi - process entire image
            self.prev_image = image_bytes

            image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
            image_np = np.array(image)
            img_h, img_w = image_np.shape[:2]

            if not roi:
                auto_roi = True
                self.prev_roi = roi = [[0, 0], [img_w - 1, img_h - 1]]

        if roi:
            x1, y1 = [int(k) for k in roi[0]]
            x2, y2 = [int(k) for k in roi[1]]
            roi_size = min(y2 - y1, x2 - x1)
        else:
            roi_size = 0

        repeat_call = repeat_image and (
            not roi or (self.prev_roi == roi and pos_points is not None) or (roi_size < 10)
        )

        context.logger.info(f"repeat_call: {repeat_call}")

        if repeat_image:
            masks = self.prev_mask
        else:
            self.prev_roi_masks = None
            self.prev_roi_bboxes = None

            flow_threshold = 0
            tile_norm_blocksize = 0
            cellprob_threshold = -10 * threshold if threshold > 0 else -0.1

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
            self.prev_mask = masks
            # cellprob = flows[-1]

        if repeat_call:
            context.logger.info(f"reusing previous roi with {len(self.prev_roi_masks)} masks left")
        else:
            self.prev_roi = roi
            context.logger.info(f"applying roi: {[x1, y1, x2, y2]}")

            roi_mask = masks[y1:y2, x1:x2]

            # masks = np.zeros_like(masks)
            # masks[y1:y2, x1:x2] = roi_mask

            cell_ids, counts = np.unique(roi_mask, return_counts=True)
            zero_idx = np.argwhere(cell_ids == 0)
            cell_ids = np.delete(cell_ids, zero_idx)
            counts = np.delete(counts, zero_idx)

            sort_idx = np.argsort(counts)
            cell_ids = cell_ids[sort_idx]
            counts = counts[sort_idx]

            self.prev_roi_masks = []
            self.prev_roi_bboxes = []
            n_cells = len(cell_ids)
            for i, cell_id in enumerate(cell_ids):
                out_mask = np.zeros_like(masks, dtype=np.uint8)
                roi_out_mask = out_mask[y1:y2, x1:x2]
                roi_out_mask[roi_mask == cell_id] = 255

                ys, xs = np.nonzero(roi_out_mask)
                xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
                bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

                context.logger.info(f"cell {i + 1} / {n_cells}: {bbox} ({counts[i]})")

                self.prev_roi_masks.append(out_mask)
                self.prev_roi_bboxes.append(bbox)

            # if not cell_ids:
            # return out_mask

            # largest_idx = int(np.argmax(counts))
            # cell_id = cell_ids[largest_idx]

            # roi_out_mask = out_mask[y1:y2, x1:x2]
            # roi_out_mask[roi_mask == cell_id] = 255

            # # out_mask[y1:y2, x1:x2] = masks[y1:y2, x1:x2, ...]
            # # out_mask[out_mask > 0] = 255
            # # cv2.normalize(out_mask, out_mask, 0, 255, cv2.NORM_MINMAX)

        if self.prev_roi_masks:
            if pos_points:
                x, y = pos_points[-1]
                match_ids = [
                    i
                    for i, bbox in enumerate(self.prev_roi_bboxes)
                    if point_is_in_box([x, y], bbox)
                ]
                if match_ids:
                    match_id = match_ids[0]
                    out_mask = self.prev_roi_masks.pop(match_id)
                    bbox = self.prev_roi_bboxes.pop(match_id)
                else:
                    context.logger.info(f"no cells match point: {[x, y]}")
                    out_mask = np.zeros_like(masks, dtype=np.uint8)
                    bbox = []
            else:
                out_mask = self.prev_roi_masks.pop()
                bbox = self.prev_roi_bboxes.pop()
        else:
            """Completed returning all of the cells from the previous processing"""
            self.prev_roi = None
            out_mask = np.zeros_like(masks, dtype=np.uint8)
            bbox = []

        if bbox:
            context.logger.info(f"returning cell with bbox: {bbox}")
        else:
            context.logger.info(f"returning empty mask")

        results = {"mask": out_mask.tolist()}
        return results

    def infer(self, event, context, threshold):

        image_bytes = event.body["image"]
        repeat_image = self.prev_image == image_bytes

        if repeat_image:
            masks = self.prev_mask
        else:
            self.prev_image = image_bytes

            image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
            image_np = np.array(image)
            flow_threshold = 0
            tile_norm_blocksize = 0
            cellprob_threshold = -10 * threshold if threshold > 0 else -0.1

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
            self.prev_mask = masks
            # cellprob = flows[-1]

        results = []

        cell_ids = np.unique(masks)
        zero_idx = np.argwhere(cell_ids == 0)
        cell_ids = np.delete(cell_ids, zero_idx)

        n_cells = len(cell_ids)

        for i, cell_id in enumerate(cell_ids):
            cell_mask = masks == cell_id
            ys, xs = np.nonzero(cell_mask)
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
            bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

            context.logger.info(f"{i + 1} / {n_cells}: {bbox}")

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
