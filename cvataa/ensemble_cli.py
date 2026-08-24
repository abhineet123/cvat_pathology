import PIL.Image
import os
import pickle
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import itertools

import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa
from cvat_sdk.api_client import exceptions
from cvat_sdk import masks

from cell_seg_params import EnsembleParams
from cell_seg_cli import CellSegCLIBase

from cell_seg_utils import (
    have_overlap,
    remove_duplicates,
    linux_path,
    get_cvat_annotations,
    add_frame_metadata,
    find_duplicate_shapes,
)


class EnsembleCLI(CellSegCLIBase):
    def __init__(
        self,
        params: EnsembleParams,
        models: list,
        name: str,
        **kwargs,
    ) -> None:
        CellSegCLIBase.__init__(self, name="ensemble", **kwargs)

        self.models = models
        self.name = name
        self.params: EnsembleParams = params

        self.multi = params.multi
        self.nms_thresh = params.nms_thresh
        self.enable_mask = params.enable_mask

        models_str = "_".join(self.models)
        cache_dir = linux_path(".cache", self.project_name, f"{self.task_name}-{models_str}")
        if self.multi:
            cache_dir = f"{cache_dir}-multi"

        model_to_shapes_pkl = linux_path(cache_dir, "model_to_shapes.pkl")
        model_to_frame_info_pkl = linux_path(cache_dir, "model_to_frame_info.pkl")

        if (
            self.params.load == 1
            and os.path.exists(cache_dir)
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
                self.retrieve_annotations_multi()
            else:
                self.retrieve_annotations()

            print(f"saving annotations to cache: {cache_dir}")
            with open(model_to_shapes_pkl, "wb") as f:
                pickle.dump(self.model_to_shapes, f)
            with open(model_to_frame_info_pkl, "wb") as f:
                pickle.dump(self.model_to_frame_info, f)

        if self.params.dups == 1:
            find_duplicate_shapes(self.model_to_shapes, remove=True)

        if self.params.dups == 2:
            find_duplicate_shapes(self.model_to_shapes, remove=False)

        assert (
            self.multi or not self.params.meta.fo
        ), "adding fiftyone_url to issues is only supported for multi-label datasets"

        if self.params.meta.cvat or self.params.meta.fo:
            add_frame_metadata(
                self.params.meta,
                self.client,
                self.job_id,
                self.task_id,
                self.task_name,
                self.name,
                self.frame_name_to_info,
                self.model_to_shapes,
            )

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
                shape["overlaps_with"] = []
                # shape = dict(
                #     model=model,
                #     id=shape["id"],
                #     bbox=shape["bbox"],
                # )

                shapes_all[model_id].append(shape)

        shapes_nms = self.perform_nms(
            shapes_all,
        )

        attributes = [("model", "model")]
        if self.params.meta.shape:
            # attributes.append(("frame_url", "url"))
            attributes.append(("url", "url"))

        self.results_cache = [
            dict(
                label_id=self.label_id,
                points=masks.encode_mask(shape["mask"], shape["bbox"]),
                attributes=[
                    dict(value=f"{shape[k1]}", spec_id=self.attribute_name_to_id[k2])
                    for k1, k2 in attributes
                    # dict(value=f"{shape['frame_url']}", spec_id=self.attribute_name_to_id["url"]),
                    # dict(
                    #     value=f"{datetime.now().strftime('%y%m%d_%H%M%S')}",
                    #     spec_id=attribute_name_to_id["notes"],
                    # ),
                ],
            )
            for shape in shapes_nms
        ]
        results = [cvataa.mask(**result) for result in self.results_cache]

        # if not self.params.load:
        # self.results_cache = results_cache

        self.update_status(context, results)
        return results

    def retrieve_annotations_multi(self):

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
            # frame_info = frame_name_to_info[frame_name]
            # self.frame_name_to_url[frame_name] = frame_info["url"]
            for shape in shapes:
                label_id = shape["label_id"]
                model = label_id_to_name[label_id]
                self.model_to_shapes[model][frame_name].append(shape)

    def retrieve_annotations(self):
        self.model_task_names = [task_name.replace(self.name, model) for model in self.models]

        self.model_task_ids = [
            self.task_name_to_obj[task_name]["_model"]["id"] for task_name in self.model_task_names
        ]

        self.model_to_shapes = {}
        self.model_to_frame_info = {}

        n_models = len(self.models)

        print("\nretrieving annotations from CVAT...")

        for model_id, (model, task_name, task_id) in enumerate(
            zip(self.models, self.model_task_names, self.model_task_ids, strict=True)
        ):
            model_str = f"model {model_id+1} / {n_models} {model}: {task_name}"

            print(f"\n{model_str}")

            frame_name_to_shapes, frame_name_to_info = get_cvat_annotations(self.client, task_id)

            self.model_to_shapes[model] = frame_name_to_shapes
            self.model_to_frame_info[model] = frame_name_to_info

        print("done")

    def perform_nms(self, shapes):
        group_pairs = list(itertools.combinations(shapes, 2))
        # for group_pair in tqdm(group_pairs):
        #     temp = list(itertools.product(*group_pair))
        #     for k in temp:
        #         shape_1, shape_2 = k
        shapes_pairs = [
            (shape_1, shape_2)
            for group_pair in group_pairs
            for shape_1, shape_2 in itertools.product(*group_pair)
            if have_overlap(shape_1, shape_2, self.enable_mask, self.nms_thresh)
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

        remove_duplicates(
            shapes_pairs,
        )

        shapes_nms = [shape for shape in shapes_flat if not shape["to_delete"]]
        return shapes_nms
