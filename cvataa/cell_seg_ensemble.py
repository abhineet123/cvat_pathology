import PIL.Image
import itertools
import numpy as np

import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa
from cvat_sdk import masks

from instanseg_cli import InstansegCLI
from stardist_cli import StardistCLI
from cellpose_cli import CellposeCLI
from cell_seg_utils import CellSegCLIBase


def box_iou_batch(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    def box_area(box):
        return (box[2] - box[0]) * (box[3] - box[1])

    area_a = box_area(boxes_a.T)
    area_b = box_area(boxes_b.T)

    top_left = np.maximum(boxes_a[:, None, :2], boxes_b[:, :2])
    bottom_right = np.minimum(boxes_a[:, None, 2:], boxes_b[:, 2:])

    area_inter = np.prod(np.clip(bottom_right - top_left, a_min=0, a_max=None), 2)

    return area_inter / (area_a[:, None] + area_b - area_inter)


def perform_nms_fast(objs, enable_mask, iou_threshold):
    assert not enable_mask, "fast nms does not support mask IOU"
    iou_threshold /= 100.0

    obj_conf_arr = np.asarray([obj["confidence"] for obj in objs])
    sort_index = np.flip(obj_conf_arr.argsort())

    boxes = np.asarray([obj["bbox"] for obj in objs])
    categories = np.asarray([obj["class_id"] for obj in objs])

    n_objs = len(objs)

    boxes = boxes[sort_index]
    categories = categories[sort_index]

    ious = box_iou_batch(boxes, boxes)
    ious = ious - np.eye(n_objs)

    keep = np.ones(n_objs, dtype=bool)

    for index, (iou, category) in enumerate(zip(ious, categories, strict=True)):
        if not keep[index]:
            continue

        condition = (iou > iou_threshold) & (categories == category)
        keep = keep & ~condition

    keep = keep[sort_index.argsort()]
    n_del = 0
    for obj, keep_ in enumerate(zip(objs, keep, strict=True)):
        if not keep_:
            obj["to_delete"] = 1
            n_del += 1
    return n_del


def get_mask_iou(mask_det, mask_gt, bb_det, bb_gt):
    x1_det, y1_det, x2_det, y2_det = bb_det
    x1_gt, y1_gt, x2_gt, y2_gt = bb_gt

    min_x, min_y = int(min(x1_det, x1_gt)), int(min(y1_det, y1_gt))
    max_x, max_y = int(max(x2_det, x2_gt)), int(max(y2_det, y2_gt))

    mask_det_ = mask_det[min_y : max_y + 1, min_x : max_x + 1]
    mask_gt_ = mask_gt[min_y : max_y + 1, min_x : max_x + 1]

    # mask_det_ = mask_det_ > 0
    # mask_gt_ = mask_gt_ > 0

    mask_union = np.logical_or(mask_det_, mask_gt_)
    n_mask_union = np.count_nonzero(mask_union)

    if n_mask_union == 0:
        return 0

    mask_inter = np.logical_and(mask_det_, mask_gt_)
    n_mask_inter = np.count_nonzero(mask_inter)

    mask_iou = n_mask_inter / n_mask_union

    return mask_iou


def get_iou(bb_det, bb_gt, xywh=False):
    if xywh:
        det_x1, det_y1, det_w, det_h = bb_det
        gt_x1, gt_y1, gt_w, gt_h = bb_gt
        det_x2, det_y2 = det_x1 + det_w - 1, det_y1 + det_h - 1
        gt_x2, gt_y2 = gt_x1 + gt_w - 1, gt_y1 + gt_h - 1
    else:
        det_x1, det_y1, det_x2, det_y2 = bb_det
        gt_x1, gt_y1, gt_x2, gt_y2 = bb_gt

        det_w, det_h = det_x2 - det_x1 + 1, det_y2 - det_y1 + 1
        gt_w, gt_h = gt_x2 - gt_x1 + 1, gt_y2 - gt_y1 + 1

    bi = [max(det_x1, gt_x1), max(det_y1, gt_y1), min(det_x2, gt_x2), min(det_y2, gt_y2)]

    iw = bi[2] - bi[0] + 1
    ih = bi[3] - bi[1] + 1

    if iw <= 0 or ih <= 0:
        return 0

    ua = (det_w * det_h) + (gt_w * gt_h) - (iw * ih)

    # compute overlap (IoU) = area of intersection / area of union
    ov = iw * ih / ua

    return ov


def find_matching_obj_pairs(
    pred_obj_pairs,
    enable_mask,
    nms_thresh,
):
    n_del = 0

    for pred_obj_pair in pred_obj_pairs:

        for obj in pred_obj_pair:
            try:
                obj["confidence"]
            except KeyError:
                obj["confidence"] = 1.0

            try:
                obj["to_delete"]
            except KeyError:
                obj["to_delete"] = 0

        obj1, obj2 = pred_obj_pair

        if obj1["to_delete"] or obj2["to_delete"]:
            continue

        if enable_mask:
            pred_iou = get_mask_iou(obj1["mask"], obj2["mask"], obj1["bbox"], obj2["bbox"])
        else:
            pred_iou = get_iou(obj1["bbox"], obj2["bbox"], xywh=False) * 100

        if pred_iou >= nms_thresh:
            n_del += 1
            # print(f'found matching object pair with iou {pred_iou:.3f}')
            if obj1["confidence"] > obj2["confidence"]:
                obj2["to_delete"] = 1

                # objs_to_delete.append(obj2['local_id'])
                # global_objs_to_delete.append(obj2['global_id'])

                # print(f'removing obj {local_id2} with score {score2} < {score1}')
            else:
                obj1["to_delete"] = 1

                # objs_to_delete.append(obj1['local_id'])
                # global_objs_to_delete.append(obj1['global_id'])

                # print(f'removing obj {local_id1} with score {score1} < {score2}')
    # return objs_to_delete, global_objs_to_delete
    return n_del


def perform_nms(objs, enable_mask=1, nms_thresh=0.3):
    pred_obj_pairs = list(itertools.product(*objs))

    n_pairs = len(pred_obj_pairs)

    n_match = find_matching_obj_pairs(
        pred_obj_pairs,
        enable_mask,
        nms_thresh,
    )

    objs_flat = [x for xs in objs for x in xs]

    for obj in objs_flat:
        try:
            obj["to_delete"]
        except KeyError:
            obj["to_delete"] = 0

    objs_nms = [
        cvataa.mask(label_id=0, points=masks.encode_mask(obj["mask"], obj["bbox"]))
        for obj in objs_flat
        if not obj["to_delete"]
    ]
    return objs_nms


class CellSegEnsembleCLI(CellSegCLIBase):
    def __init__(self, task_name, n_frames, verbose=True) -> None:
        CellSegCLIBase.__init__(self, task_name, n_frames, verbose, "Ensemble")
        self.predictors = [
            InstansegCLI(task_name, n_frames),
            StardistCLI(task_name, n_frames),
            CellposeCLI(task_name, n_frames),
        ]

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: PIL.Image.Image
    ) -> list[models.LabeledShapeRequest]:
        self.update_status(context)
        results_all = []
        for predictor in self.predictors:
            results = predictor.detect(context, image, return_raw=True)
            results_all.append(results)

        results_nms = perform_nms(results_all)

        return results_nms
