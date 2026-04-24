import PIL.Image
import os
import pickle
import numpy as np
from tqdm import tqdm
from collections import defaultdict


import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa
from cvat_sdk import masks

from cell_seg_utils import (
    EnsembleParams,
    CellSegCLIBase,
    perform_nms,
    linux_path,
    get_cvat_annotations,
)


class EnsembleCLI(CellSegCLIBase):
    def __init__(
        self,
        params: EnsembleParams,
        models: list,
        name: str,
        client,
        task_name: str,
        label_name: str,
        task_name_to_obj: dict,
        n_frames: int,
        verbose=True,
        **kwargs,
    ) -> None:
        CellSegCLIBase.__init__(self, task_name, label_name, n_frames, verbose, "Ensemble")

        self.models = models
        self.name = name
        self.params = params

        self.multi = params.multi
        self.nms_thresh = params.nms_thresh

        self.client = client
        self.task_name_to_obj = task_name_to_obj

        models_str = "_".join(self.models)
        cache_dir = linux_path(".cache", f"{task_name}-{models_str}")
        if self.multi:
            cache_dir = f"{cache_dir}-multi"

        model_to_shapes_pkl = linux_path(cache_dir, "model_to_shapes.pkl")
        model_to_frame_info_pkl = linux_path(cache_dir, "model_to_frame_info.pkl")

        if (
            os.path.exists(cache_dir)
            and os.path.isfile(model_to_shapes_pkl)
            and os.path.isfile(model_to_frame_info_pkl)
        ):
            print(f"loading annotations from cache: {cache_dir}")
            with open(model_to_shapes_pkl, "rb") as f:
                self.model_to_shapes = pickle.load(f)
            with open(model_to_frame_info_pkl, "rb") as f:
                self.model_to_frame_info = pickle.load(f)
        else:
            os.makedirs(cache_dir, exist_ok=True)
            if self.multi:
                self.load_annotations_multi()
            else:
                self.load_annotations()

            print(f"saving annotations to cache: {cache_dir}")
            with open(model_to_shapes_pkl, "wb") as f:
                pickle.dump(self.model_to_shapes, f)
            with open(model_to_frame_info_pkl, "wb") as f:
                pickle.dump(self.model_to_frame_info, f)

    def load_annotations_multi(self):

        # projects_dict = [project.__dict__ for project in self.client.projects.list()]
        # project_id_to_dict = {
        #     project["_model"]["id"]: project["_model"] for project in projects_dict
        # }

        task_name = self.task_name.replace(self.name, "multi")
        task_dict = self.task_name_to_obj[task_name]["_model"]
        task_id = task_dict["id"]
        # project_id = task_dict["project_id"]
        # project_dict = project_id_to_dict[project_id]

        task = self.client.tasks.retrieve(task_id)
        labels = task.get_labels()
        label_id_to_name = {label["id"]: label["name"] for label in labels}

        print(f"get_cvat_annotations: {task_name}")
        frame_name_to_shapes, frame_name_to_info = get_cvat_annotations(
            self.client,
            task_id,
        )

        self.model_to_shapes = {model: defaultdict(list) for model in self.models}
        self.model_to_frame_info = {model: frame_name_to_info for model in self.models}
        for frame_name, shapes in frame_name_to_shapes.items():
            for shape in shapes:
                label_id = shape["label_id"]
                model = label_id_to_name[label_id]
                self.model_to_shapes[model][frame_name].append(shape)

    def load_annotations(self):
        self.model_task_names = [task_name.replace(self.name, model) for model in self.models]

        self.model_task_ids = [
            self.task_name_to_obj[task_name]["_model"]["id"] for task_name in self.model_task_names
        ]

        self.model_to_shapes = {}
        self.model_to_frame_info = {}

        n_models = len(self.models)

        print("\n\nloading annotations from CVAT...")

        for model_id, (model, task_name, task_id) in enumerate(
            zip(self.models, self.model_task_names, self.model_task_ids, strict=True)
        ):
            model_str = f"model {model_id+1} / {n_models} {model}: {task_name}"

            print(f"\n{model_str}")

            frame_name_to_shapes, frame_name_to_info = get_cvat_annotations(self.client, task_id)

            self.model_to_shapes[model] = frame_name_to_shapes
            self.model_to_frame_info[model] = frame_name_to_info

        print("done")

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: PIL.Image.Image
    ) -> list[models.LabeledShapeRequest]:
        shapes_all = [[] for _ in self.models]
        for model_id, model in enumerate(self.models):
            shapes = self.model_to_shapes[model][context.frame_name]
            frame_info = self.model_to_frame_info[model][context.frame_name]
            frame_w, frame_h = frame_info["width"], frame_info["height"]

            for shape in shapes:
                pts = shape["points"]
                obj_mask = masks.decode_mask(pts, image_width=frame_w, image_height=frame_h)
                ys, xs = np.nonzero(obj_mask)
                if not ys.size or not xs.size:
                    continue
                xmin, ymin, xmax, ymax = (
                    np.amin(xs),
                    np.amin(ys),
                    np.amax(xs),
                    np.amax(ys),
                )
                shape["area"] = int((ymax - ymin) * (xmax - xmin))
                if shape["area"] <= 1:
                    continue

                shape["mask"] = obj_mask
                shape["bbox"] = [int(xmin), int(ymin), int(xmax), int(ymax)]
                shape["to_delete"] = 0
                shape["model"] = model
                # shape = dict(
                #     model=model,
                #     id=shape["id"],
                #     bbox=shape["bbox"],
                # )

                shapes_all[model_id].append(shape)

        shapes_nms = perform_nms(shapes_all, nms_thresh=self.nms_thresh)

        self.update_status(context, shapes_nms)
        return shapes_nms
