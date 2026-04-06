import os
import cv2
import itertools
from PIL import Image
import numpy as np
from tqdm import tqdm

from cvat_sdk import masks, auto_annotation
import cvat_sdk.auto_annotation as cvataa
import cvat_sdk.models as models


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
    def __init__(self, task_name, n_frames, verbose, name) -> None:
        self.task_name = task_name
        self.n_frames = n_frames
        self.verbose = verbose
        self.name = name
        self.frame_id = 0
        self.pbar = tqdm(total=n_frames)

    @property
    def spec(self) -> cvataa.DetectionFunctionSpec:
        return cvataa.DetectionFunctionSpec(labels=[cvataa.label_spec("nucleus", 0, type="mask")])

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
