import os

import numpy as np
from tqdm import tqdm

import compress_json

from cvat_sdk import Client
from cvat_sdk import masks, auto_annotation
import cvat_sdk.auto_annotation as cvataa

from cell_seg_utils import (
    linux_path,
)


class CellSegCLIBase:
    def __init__(
        self, task_name, client: Client, task_name_to_obj, label_name, n_frames, verbose, name
    ) -> None:
        self.task_name = task_name
        self.n_frames = n_frames
        self.verbose = verbose
        self.name = name
        self.frame_id = 0

        if self.verbose:
            self.pbar = None
        else:
            self.pbar = tqdm(
                total=n_frames,
                position=0,
                leave=True,
                # file=sys.stdout,
            )

        self.client: Client = client
        self.task_name_to_obj = task_name_to_obj
        self.task_id = self.task_name_to_obj[self.task_name]["_model"]["id"]
        self.task = self.client.tasks.retrieve(self.task_id)

        self.label_name = label_name
        self.labels = [label.to_dict() for label in self.task.get_labels()]
        self.label_id_to_dict = {label["id"]: label for label in self.labels}
        self.label_name_to_id = {label["name"]: label["id"] for label in self.labels}
        self.label_id = self.label_name_to_id[label_name]
        self.label_dict = self.label_id_to_dict[self.label_id]

        self.attributes = self.label_dict["attributes"]
        self.attribute_name_to_id = {
            attribute["name"]: attribute["id"] for attribute in self.attributes
        }

        self.label_specs = [cvataa.label_spec(**label) for label in self.labels]
        self.det_func_spec = cvataa.DetectionFunctionSpec(labels=self.label_specs)

        self.results_cache = None
        self.frame_name_to_cache = {}

        self.project_name = self.task_name_to_obj[self.task_name]["_model"]["project_name"]
        self.json_dir = linux_path(".cache", self.project_name, self.name)
        os.makedirs(self.json_dir, exist_ok=True)

        frames_info = self.task.get_frames_info()
        self.frame_name_to_info = {frame_info["name"]: frame_info for frame_info in frames_info}
        for frame_id, frame_info in enumerate(frames_info):
            frame_info["id"] = frame_id

        jobs = self.task.get_jobs()

        assert len(jobs) == 1, "multiple jobs found in task"

        self.job = jobs[0]
        self.job_id = self.job.id

    @property
    def spec(self) -> cvataa.DetectionFunctionSpec:
        return self.det_func_spec

    def instance_mask_to_cells(
        self,
        instance_mask: np.ndarray,
    ):
        results = []

        cell_ids = np.unique(instance_mask)
        n_cells = len(cell_ids) - 1

        pbar = cell_ids
        # pbar = tqdm(cell_ids, total=n_cells)

        self.results_cache = []

        for cell_id in pbar:
            if cell_id == 0:
                continue

            cell_mask = instance_mask == cell_id
            ys, xs = np.nonzero(cell_mask)
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
            bbox = [float(xmin), float(ymin), float(xmax), float(ymax)]

            if xmax <= xmin or ymax <= ymin:
                continue

            # cell_mask_uint8 = cell_mask.astype(np.uint8) * 255
            # contour_cv = to_contour_cv(cell_mask_uint8)
            # contour = to_contour(cell_mask_uint8).ravel().tolist()

            # result_raw = {
            #     "mask": cell_mask,
            #     "bbox": bbox,
            # }

            points = masks.encode_mask(cell_mask, bbox)
            result_dict = dict(
                label_id=self.label_id,
                points=points,
                attributes=[
                    dict(value=f"{self.name}", spec_id=self.attribute_name_to_id["model"]),
                    # dict(
                    #     value=f"{datetime.now().strftime('%y%m%d_%H%M%S')}",
                    #     spec_id=attribute_name_to_id["notes"],
                    # ),
                ],
            )

            result = auto_annotation.mask(**result_dict)
            results.append(result)

            self.results_cache.append(result_dict)

        return results

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

        if self.results_cache is not None:
            self.frame_name_to_cache[context.frame_name] = self.results_cache
            if self.frame_id == self.n_frames:
                if not self.verbose:
                    self.pbar.close()
                json_path = linux_path(self.json_dir, f"{self.task_name}.json.gz")
                print(f"saving results cache to {json_path}")
                json_kwargs = dict(indent=4)
                compress_json.dump(self.frame_name_to_cache, json_path, json_kwargs=json_kwargs)
