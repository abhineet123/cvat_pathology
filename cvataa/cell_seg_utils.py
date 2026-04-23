import os
import cv2
import itertools
from PIL import Image
import numpy as np
from tqdm import tqdm
from collections import defaultdict

from cvat_sdk import masks, auto_annotation
import cvat_sdk.auto_annotation as cvataa
import cvat_sdk.models as models


class EnsembleParams:
    def __init__(self):
        self.sfx = ""
        self.nms_thresh = 0.3
        self.multi = 1


class Filter:
    def __init__(self):
        self.iall = []
        self.iany = []
        self.eall = []
        self.eany = []

    def apply(self, relevant_task_names):
        if self.iall:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if all(str(k) in task_name for k in self.iall)
            ]
        if self.iany:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if any(str(k) in task_name for k in self.iany)
            ]

        if self.eall:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if not all(str(k) in task_name for k in self.eall)
            ]
        if self.eany:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if not any(str(k) in task_name for k in self.eany)
            ]
        return relevant_task_names


class CVATAuth:
    def __init__(self):
        self.host = ""
        self.access_token = ""
        self.username = ""
        self.pwd = ""

    def to_cfg(self):
        if not self.host:
            try:
                self.host = os.environ["CVAT_HOST"]
            except KeyError:
                raise AssertionError("cvat host must be provided")

        if not self.access_token:
            try:
                self.access_token = os.environ["CVAT_ACCESS_TOKEN"]
            except KeyError:
                if not self.username and not self.pwd:
                    try:
                        self.username = os.environ["CVAT_USERNAME"]
                        self.pwd = os.environ["CVAT_PWD"]
                    except KeyError:
                        raise AssertionError(
                            "either cvat access_token or username / pwd must be provided"
                        )

        client_cfg = dict(host=self.host)
        if self.access_token:
            client_cfg.update(dict(access_token=self.access_token))
        else:
            client_cfg.update(dict(credentials=(self.username, self.pwd)))

        return client_cfg


class CellSegCLIBase:
    def __init__(self, task_name, label_name, n_frames, verbose, name) -> None:
        self.task_name = task_name
        self.n_frames = n_frames
        self.verbose = verbose
        self.name = name
        self.frame_id = 0
        # self.label_id = label_id
        self.label_name = label_name
        self.pbar = tqdm(total=n_frames)

    @property
    def spec(self) -> cvataa.DetectionFunctionSpec:
        return cvataa.DetectionFunctionSpec(
            labels=[cvataa.label_spec(self.label_name, 0, type="mask")]
        )

    def update_status(self, context: cvataa.DetectionFunctionContext, objs):
        self.frame_id += 1
        n_objs = len(objs)
        assert (
            self.frame_id <= self.n_frames
        ), f"frame_id: {self.frame_id} exceeds n_frames: {self.n_frames}"

        if self.verbose:
            print(
                f"{self.name}: {self.task_name} frame {self.frame_id} / {self.n_frames}: {context.frame_name}"
            )
        else:
            self.pbar.set_description(f"frame: {context.frame_name} n_objs: {n_objs}")
            self.pbar.update(1)


class LoadAnnotations(CellSegCLIBase):
    def __init__(self, load_dir, task_name, n_frames, verbose=True) -> None:
        CellSegCLIBase.__init__(self, task_name, n_frames, verbose, "LoadAnnotations")
        self.load_dir = load_dir
        image_exts = ["bmp", "png", "tif"]
        self.mask_paths = [
            os.path.join(self.load_dir, k)
            for k in os.listdir(self.load_dir)
            if any(k.lower().endswith(f".{_ext}") for _ext in image_exts)
        ]
        self.mask_name_to_path = {
            os.path.splitext(os.path.basename(mask_path))[0]: mask_path
            for mask_path in self.mask_paths
        }
        all_rgb_cols = list(itertools.product(range(256), repeat=3))
        self.rgb_cols_to_id = {rgb_col: i for i, rgb_col in enumerate(all_rgb_cols) if i > 0}

        print(f"loading annotations from {self.load_dir}")

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: Image.Image, return_raw=False
    ) -> list[models.LabeledShapeRequest]:

        frame_name = os.path.splitext(os.path.basename(context.frame_name))[0]

        try:
            mask_path = self.mask_name_to_path[frame_name]
        except KeyError:
            print(f"using empty mask for nonexistent frame: {frame_name} ")
            results = []
        else:
            mask_rgb = np.asarray(Image.open(mask_path))
            mask_id = mask_rgb_to_id(mask_rgb, self.rgb_cols_to_id)
            results = instance_mask_to_cells(mask_id, return_raw)

        self.update_status(context, results)
        return results


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


def mask_pts_to_img(mask_pts, img_h, img_w):
    mask_img = np.zeros((img_h, img_w), dtype=np.uint8)
    mask_img = cv2.fillPoly(
        mask_img,
        np.array(
            [
                mask_pts,
            ],
            dtype=np.int32,
        ),
        1,
    )

    # mask_img_vis = (mask_img * 255).astype(np.uint8)
    # mask_img_vis = resize_ar(mask_img_vis, 1280, 720)
    # cv2.imshow('mask_img_vis', mask_img_vis)
    # cv2.waitKey(0)

    bin_mask_img = mask_img.astype(bool)

    return bin_mask_img


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


def get_mask_ioa(mask_det, mask_gt, bb_det, bb_gt):
    x1_det, y1_det, x2_det, y2_det = bb_det
    x1_gt, y1_gt, x2_gt, y2_gt = bb_gt

    min_x, min_y = int(min(x1_det, x1_gt)), int(min(y1_det, y1_gt))
    max_x, max_y = int(max(x2_det, x2_gt)), int(max(y2_det, y2_gt))

    mask_det_ = mask_det[min_y : max_y + 1, min_x : max_x + 1]
    mask_gt_ = mask_gt[min_y : max_y + 1, min_x : max_x + 1]

    mask_inter = np.logical_and(mask_det_, mask_gt_)
    n_mask_inter = np.count_nonzero(mask_inter)

    if n_mask_inter == 0:
        return 0

    area_det = np.count_nonzero(mask_det)
    area_gt = np.count_nonzero(mask_gt)

    min_area = min(area_det, area_gt)

    mask_ioa = n_mask_inter / min_area

    return mask_ioa


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


def get_ioa(bb_det, bb_gt, xywh=False):
    """
    compute overlap (IoA) = area of intersection / area of smaller box
    """

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

    area_det = det_w * det_h
    area_gt = gt_w * gt_h

    min_area = min(area_det, area_gt)

    ov = iw * ih / min_area

    return ov


def find_matching_obj_pairs(
    obj_pairs,
    enable_mask,
    nms_thresh,
):
    n_del = 0

    for obj_pair in obj_pairs:

        obj1, obj2 = obj_pair

        if obj1["to_delete"] or obj2["to_delete"]:
            continue

        if enable_mask:
            """if a small detection is completely covered by a large detection, the small one can escape the filtering process since the the area of union is equal to the area of the large detection while the area of intersection is equal to the area of the small detection so if the latter is small enough, the ratio between them might will be less than nms_thresh"""
            # iou = get_mask_iou(obj1["mask"], obj2["mask"], obj1["bbox"], obj2["bbox"])

            iou = get_mask_ioa(obj1["mask"], obj2["mask"], obj1["bbox"], obj2["bbox"])
        else:
            # iou = get_iou(obj1["bbox"], obj2["bbox"], xywh=False)
            iou = get_ioa(obj1["bbox"], obj2["bbox"], xywh=False)

        if iou >= nms_thresh:
            models = [obj1["model"], obj2["model"]]
            if "instanseg" in models and "cellpose" in models:
                """cellpose has less tight detections than instanseg (i.e. it can include an area of FP around the nucleus)
                so keep instanseg nucleus when it conflicts with cellpose nucleus"""
                if obj1["model"] == "instanseg":
                    obj2["to_delete"] = 1
                else:
                    obj1["to_delete"] = 1
            else:
                """keep the nucleus with greater area assuming that models (e.g. stardist) are prone to detecting partial nuclei"""
                if obj1["area"] > obj2["area"]:
                    obj2["to_delete"] = 1
                else:
                    obj1["to_delete"] = 1


def get_cvat_annotations(client, task_id):

    # print(f"{model_str}: retrieve task")
    task = client.tasks.retrieve(task_id)
    # print(f"{model_str}: get_frames_info")
    frames_info = task.get_frames_info()

    frame_name_to_info = {frame_info["name"]: frame_info for frame_info in frames_info}
    annotations = task.get_annotations()

    shapes = annotations["shapes"]
    # frames_dicts = [frame_info.to_dict() for frame_info in frames_info]
    frame_name_to_shapes = defaultdict(list)
    pbar = tqdm(shapes, position=0, leave=True)
    for shape in pbar:
        frame_id = shape["frame"]
        frame_name = frames_info[frame_id]["name"]
        frame_name_to_shapes[frame_name].append(shape.to_dict())
        # pbar.set_description(
        #     f"{model_str} frame {frame_id} {frame_name} {len(frame_name_to_shapes[frame_name])} objs"
        # )
    return frame_name_to_shapes, frame_name_to_info


def have_overlap(bbox1, bbox2):
    x1min, y1min, x1max, y1max = bbox1
    x2min, y2min, x2max, y2max = bbox2
    return x1min < x2max and x2min < x1max and y1min < y2max and y2min < y1max


def perform_nms(shapes, enable_mask=1, nms_thresh=0.3):
    group_pairs = list(itertools.combinations(shapes, 2))
    # for group_pair in tqdm(group_pairs):
    #     temp = list(itertools.product(*group_pair))
    #     for k in temp:
    #         shape_1, shape_2 = k
    shapes_pairs = [
        (shape_1, shape_2)
        for group_pair in group_pairs
        for shape_1, shape_2 in itertools.product(*group_pair)
        if have_overlap(shape_1["bbox"], shape_2["bbox"])
    ]

    shapes_flat = [x for xs in shapes for x in xs]

    # shapes_groups = list(itertools.product(*shapes))
    # shapes_pairs2 = [
    #     (shape_1, shape_2)
    #     for shapes_group in tqdm(shapes_groups)
    #     for shape_1, shape_2 in itertools.combinations(shapes_group, 2)
    #     if have_overlap(shape_1["bbox"], shape_2["bbox"])
    # ]
    # n_pairs = len(shapes_pairs)

    find_matching_obj_pairs(
        shapes_pairs,
        enable_mask,
        nms_thresh,
    )

    shapes_nms = [
        cvataa.mask(
            label_id=0,
            points=masks.encode_mask(shape["mask"], shape["bbox"]),
            model=f"ensemble-{shape['model']}",
        )
        for shape in shapes_flat
        if not shape["to_delete"]
    ]
    return shapes_nms


def draw_box(
    frame,
    box,
    _id=None,
    color=(255, 255, 255),
    thickness=1,
    transparency=0.0,
    xywh=True,
    norm=False,
):
    """
    :type frame: np.ndarray
    :type _id: int | str | None
    :param color: indexes into col_bgr
    :type color: str
    :type thickness: int
    :type is_dotted: int
    :type transparency: float
    :rtype: None
    """
    if not isinstance(box, np.ndarray):
        box = np.asarray(box)

    if np.any(np.isnan(box)):
        print("invalid location provided: {}".format(box))
        return

    if isinstance(box, np.ndarray):
        box = list(box.squeeze())

    if xywh:
        pt1 = (box[0], box[1])
        pt2 = (box[0] + box[2], box[1] + box[3])
    else:
        pt1 = (box[0], box[1])
        pt2 = (box[2], box[3])

    img_h, img_w = frame.shape[:2]

    if norm:
        pt1 = (pt1[0] * img_w, pt1[1] * img_h)
        pt2 = (pt2[0] * img_w, pt2[1] * img_h)

    pt1 = tuple(map(int, pt1))
    pt2 = tuple(map(int, pt2))

    if transparency > 0:
        _frame = np.copy(frame)
    else:
        _frame = frame

    cv2.rectangle(_frame, pt1, pt2, color, thickness=thickness)

    if transparency > 0:
        frame[pt1[1] : pt2[1], pt1[0] : pt2[0], ...] = (
            frame[pt1[1] : pt2[1], pt1[0] : pt2[0], ...].astype(np.float32) * (1 - transparency)
            + _frame[pt1[1] : pt2[1], pt1[0] : pt2[0], ...].astype(np.float32) * transparency
        ).astype(frame.dtype)

    if _id is not None:
        font_line_type = cv2.LINE_AA
        cv2.putText(
            frame,
            str(_id),
            (int(box[0] - 1), int(box[1] - 1)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            font_line_type,
        )


def linux_path(*args, **kwargs):
    return os.path.join(*args, **kwargs).replace(os.sep, "/")


def hex_to_rgb(hex):
    return tuple(int(hex[i : i + 2], 16) for i in (1, 3, 5))


def mask_rgb_to_id(mask_rgb, rgb_cols_to_id):
    unique_rgb_vals = np.unique(mask_rgb.reshape(-1, mask_rgb.shape[2]), axis=0)
    unique_ids = list(rgb_cols_to_id[tuple(rgb_val)] for rgb_val in unique_rgb_vals)

    mask_h, mask_w = mask_rgb.shape[:2]
    mask_id = np.zeros((mask_h, mask_w), dtype=np.int32)
    for rgb_val, unique_id in zip(unique_rgb_vals, unique_ids, strict=True):
        if unique_id == 0:
            continue
        mask_id[mask_rgb == rgb_val] = unique_id

    return mask_id


def to_str(relevant_task_names):
    return "\n".join(relevant_task_names)


def instance_mask_to_cells(instance_mask: np.ndarray, return_raw: bool):
    results = []

    cell_ids = np.unique(instance_mask)
    n_cells = len(cell_ids) - 1

    pbar = cell_ids
    # pbar = tqdm(cell_ids, total=n_cells)

    for cell_id in pbar:
        if cell_id == 0:
            continue

        cell_mask = instance_mask == cell_id
        ys, xs = np.nonzero(cell_mask)
        xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
        bbox = [float(xmin), float(ymin), float(xmax), float(ymax)]

        if xmax <= xmin or ymax <= ymin:
            continue

        if return_raw:
            result = {
                "mask": cell_mask,
                "bbox": bbox,
            }
        else:
            points = masks.encode_mask(cell_mask, bbox)
            result = auto_annotation.mask(label_id=0, points=points)

        results.append(result)

    return results
