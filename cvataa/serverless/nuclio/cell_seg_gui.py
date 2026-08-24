import numpy as np
import base64
import cv2
import io
from skimage.measure import approximate_polygon, find_contours
from PIL import Image


def to_contour_cv_old(mask_img_gs):
    contour_pts, _ = cv2.findContours(mask_img_gs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    contour_pts = contour_pts[0]
    contour_pts = contour_pts.squeeze().tolist()
    contour_pts_flat = [x for xs in contour_pts for x in xs]
    return contour_pts_flat


def to_contour_cv(mask_img_gs):

    contour_raw = cv2.findContours(mask_img_gs, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_sorted = sorted(list(contour_raw[0]), key=lambda x: x.size, reverse=True)
    contour = np.squeeze(contours_sorted[0].astype("int32"))

    # contour_cv = to_contour_cv(cell_mask_uint8)
    # contour_ski = to_contour(cell_mask_uint8)

    if contour.size < 6:
        """a valid polygon must be at least a triangle"""
        return None

    contour = contour.squeeze().tolist()
    contour_flat = [x for xs in contour for x in xs]
    return contour_flat


def to_contour_sk(mask):
    contours = find_contours(mask)
    contour = contours[0]
    contour = np.flip(contour, axis=1)
    contour = approximate_polygon(contour, tolerance=2.5)
    contour_flat = contour.ravel().tolist()
    return contour_flat


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


class CellSegGUI:
    def __init__(self):
        self.image = None
        self.threshold = None
        self.mask = None

        self.roi = None
        self.pos_point = None
        self.neg_point = None
        self.roi_masks = []
        self.roi_bboxes = []

    def get_instance_mask(self, image, threshold):
        raise NotImplementedError

    def get_cell_masks_with_roi(self, mask, roi_bbox, context):

        x1, y1, x2, y2 = roi_bbox

        roi_mask = mask[y1:y2, x1:x2]

        cell_ids, counts = np.unique(roi_mask, return_counts=True)
        invalid_idx = np.argwhere(cell_ids <= 0)
        cell_ids = np.delete(cell_ids, invalid_idx)
        counts = np.delete(counts, invalid_idx)

        sort_idx = np.argsort(counts)
        cell_ids = cell_ids[sort_idx]
        counts = counts[sort_idx]

        self.roi_masks = []
        self.roi_bboxes = []
        n_cells = len(cell_ids)
        for i, cell_id in enumerate(cell_ids):
            out_mask = np.zeros_like(mask, dtype=np.uint8)
            roi_out_mask = out_mask[y1:y2, x1:x2]
            roi_out_mask[roi_mask == cell_id] = 255

            ys, xs = np.nonzero(roi_out_mask)
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
            bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

            context.logger.info(f"cell {i + 1} / {n_cells}: {bbox} ({counts[i]})")

            self.roi_masks.append(out_mask)
            self.roi_bboxes.append(bbox)

        # if not cell_ids:
        # return out_mask

        # largest_idx = int(np.argmax(counts))
        # cell_id = cell_ids[largest_idx]

        # roi_out_mask = out_mask[y1:y2, x1:x2]
        # roi_out_mask[roi_mask == cell_id] = 255

        # # out_mask[y1:y2, x1:x2] = mask[y1:y2, x1:x2, ...]
        # # out_mask[out_mask > 0] = 255
        # # cv2.normalize(out_mask, out_mask, 0, 255, cv2.NORM_MINMAX)

    def infer_with_roi(self, event, context, threshold, roi):

        self.context = context
        self.event = event

        data = event.body
        pos_points = data.get("pos_points", None)
        neg_points = data.get("neg_points", None)
        image_bytes = data["image"]

        repeat_image = self.image == image_bytes and self.threshold == threshold

        context.logger.info(f"\nrepeat_image: {repeat_image}")
        context.logger.info(f"pos_points: {pos_points}")
        context.logger.info(f"neg_points: {neg_points}")
        context.logger.info(f"roi: {roi}")
        context.logger.info(f"self.prev_roi : {self.roi }")

        auto_roi = False
        if not repeat_image:
            # first call on this image without roi - process entire image
            self.image = image_bytes
            self.threshold = threshold

            image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
            image_np = np.array(image)
            img_h, img_w = image_np.shape[:2]

            if not roi:
                auto_roi = True
                self.roi = roi = [[0, 0], [img_w - 1, img_h - 1]]

        if roi:
            x1, y1 = [int(k) for k in roi[0]]
            x2, y2 = [int(k) for k in roi[1]]

        repeat_call = repeat_image and self.roi is not None and (not roi or self.roi == roi)

        context.logger.info(f"repeat_call: {repeat_call}")

        if repeat_image:
            mask = self.mask
        else:
            self.roi_masks = None
            self.roi_bboxes = None

            self.mask = mask = self.get_instance_mask(image_np, threshold)

        if repeat_call:
            context.logger.info(f"reusing previous roi with {len(self.roi_masks)} masks left")
        else:
            context.logger.info(f"applying roi: {[x1, y1, x2, y2]}")
            self.roi = roi
            self.get_cell_masks_with_roi(mask, [x1, y1, x2, y2], context)

        if self.roi_masks:
            if pos_points and self.pos_point != pos_points[-1]:
                x, y = self.pos_point = pos_points[-1]
                match_ids = [
                    i for i, bbox in enumerate(self.roi_bboxes) if point_is_in_box([x, y], bbox)
                ]
                if match_ids:
                    match_id = match_ids[0]
                    out_mask = self.roi_masks.pop(match_id)
                    bbox = self.roi_bboxes.pop(match_id)
                else:
                    context.logger.info(f"no cells match point: {[x, y]}")
                    out_mask = np.zeros_like(mask, dtype=np.uint8)
                    bbox = []
            else:
                if neg_points:
                    neg_point = neg_points[-1]
                    if neg_point == self.neg_point:
                        context.logger.info(f"both pos_point and neg_point are repeated")
                    else:
                        self.neg_point = neg_point
                        out_mask = self.roi_masks.pop()
                        bbox = self.roi_bboxes.pop()
                        context.logger.info(f"returning largest unused cell: {bbox}")

                out_mask = self.roi_masks.pop()
                bbox = self.roi_bboxes.pop()
        else:
            """Completed returning all of the cells from the previous processing"""
            self.roi = None
            out_mask = np.zeros_like(mask, dtype=np.uint8)
            bbox = []

        if bbox:
            context.logger.info(f"returning cell with bbox: {bbox}")
            # contour_cv = to_contour_cv(out_mask)
            # context.logger.info(f"pts in contour_cv: {len(contour_cv)}")
            # contour = to_contour(out_mask).ravel().tolist()
            # context.logger.info(f"pts in contour: {len(contour)}")

        else:
            context.logger.info(f"returning empty mask")
            # contour_cv = []

        results = {
            "mask": out_mask.tolist(),
            # "points": contour_cv,
        }
        return results

    def infer(self, event, context, threshold):

        self.context = context
        self.event = event

        image_bytes = event.body["image"]
        repeat_image = self.image == image_bytes and self.threshold == threshold

        if repeat_image:
            mask = self.mask
        else:
            self.image = image_bytes
            self.threshold = threshold

            image = Image.open(io.BytesIO(base64.b64decode(image_bytes)))
            image_np = np.array(image)

            self.mask = mask = self.get_instance_mask(image_np, threshold)

        results = []

        cell_ids = np.unique(mask)
        invalid_idx = np.argwhere(cell_ids <= 0)
        cell_ids = np.delete(cell_ids, invalid_idx)
        n_cells = len(cell_ids)

        for i, cell_id in enumerate(cell_ids):
            cell_mask = mask == cell_id
            ys, xs = np.nonzero(cell_mask)
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
            bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

            cell_mask_uint8 = cell_mask.astype(np.uint8) * 255
            cvat_mask = to_cvat_mask(bbox, cell_mask_uint8)
            contour = to_contour_cv(cell_mask_uint8)
            # contour = to_contour_sk(cell_mask_uint8)

            if contour is None:
                continue

            context.logger.info(f"{i + 1} / {n_cells}: {bbox} contour: {len(contour)}")

            result = {
                "confidence": str(1),
                "label": "nucleus",
                "type": "mask",
                "points": contour,
                "mask": cvat_mask,
            }

            results.append(result)
        return results
