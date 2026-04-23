import PIL.Image
import os
import pickle
import numpy as np
from tqdm import tqdm

import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa
from cvat_sdk import masks

from cell_seg_utils import CellSegCLIBase, perform_nms, linux_path, get_cvat_annotations


class EnsembleCLI(CellSegCLIBase):
    def __init__(
        self,
        models: list,
        name: str,
        client,
        task_name: str,
        label_name: str,
        task_name_to_obj: dict,
        n_frames: int,
        nms_thresh: float,
        verbose=True,
        **kwargs,
    ) -> None:
        CellSegCLIBase.__init__(self, task_name, label_name, n_frames, verbose, "Ensemble")

        self.models = models
        self.name = name
        self.nms_thresh = nms_thresh
        self.client = client
        self.task_name_to_obj = task_name_to_obj

        self.model_task_names = [task_name.replace(name, model) for model in self.models]

        self.task_name_to_id = {
            task_name: task_name_to_obj[task_name]["_model"]["id"]
            for task_name in self.model_task_names
        }

        models_str = "_".join(self.models)
        cache_dir = linux_path(".cache", f"{task_name}-{models_str}")
        if os.path.exists(cache_dir):
            print(f"loading annotations from cache: {cache_dir}")
            with open(linux_path(cache_dir, "model_to_shapes.pkl"), "rb") as f:
                self.model_to_shapes = pickle.load(f)
            with open(linux_path(cache_dir, "model_to_frame_info.pkl"), "rb") as f:
                self.model_to_frame_info = pickle.load(f)
        else:
            os.makedirs(cache_dir, exist_ok=False)
            self.load_annotations()

            print(f"saving annotations to cache: {cache_dir}")
            with open(linux_path(cache_dir, "model_to_shapes.pkl"), "wb") as f:
                pickle.dump(self.model_to_shapes, f)
            with open(linux_path(cache_dir, "model_to_frame_info.pkl"), "wb") as f:
                pickle.dump(self.model_to_frame_info, f)

    def load_annotations(self):
        self.model_to_shapes = {}
        self.model_to_frame_info = {}

        n_models = len(self.models)

        print("\n\nloading annotations from CVAT...")

        for model_id, (model, task_name) in enumerate(
            zip(self.models, self.model_task_names, strict=True)
        ):
            model_str = f"model {model_id+1} / {n_models} {model}: {task_name}"

            frame_name_to_shapes, frame_name_to_info = get_cvat_annotations(
                task_name, self.task_name_to_id, self.client
            )

            print(f"\n{model_str}")

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
