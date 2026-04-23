import numpy as np

# np.set_printoptions(legacy="1.25")

import functools
import paramparse
from tqdm import tqdm

from cvat_sdk import make_client, datasets
import cvat_sdk.auto_annotation as cvataa

# from cvat_sdk.core import progress

from cell_seg_utils import (
    EnsembleParams,
    CVATAuth,
    Filter,
    LoadAnnotations,
    to_str,
    linux_path,
    get_cvat_annotations,
)


class Params(paramparse.CFG):
    def __init__(self):
        paramparse.CFG.__init__(self)

        self.auth = CVATAuth()
        self.filter = Filter()

        self.models = []
        self.load = ""
        self.load_root = "/data/PDL1-2026-Tiles/vis"
        self.mask_dir_name = "masks-cellvit"
        self.multi = 0
        self.reset = 1

        self.ensemble = EnsembleParams()


def main():
    params: Params = paramparse.process(Params)

    if params.multi:
        params.reset = 0

    client_cfg = params.auth.to_cfg()

    if params.load:
        params.load = ",".split(params.load)
        assert len(params.load) == len(params.models), "load - models len mismatch"

        if params.load_root:
            params.load = [linux_path(params.load_root, k) for k in params.load]
        if params.mask_dir_name:
            params.load = [linux_path(k, params.mask_dir_name) for k in params.load]

    with make_client(**client_cfg) as client:
        tasks_dict = [task.__dict__ for task in client.tasks.list()]

        task_name_to_id = {task["_model"]["name"]: task["_model"]["id"] for task in tasks_dict}
        task_name_to_dict = {task["_model"]["name"]: task["_model"] for task in tasks_dict}
        task_name_to_obj = {task["_model"]["name"]: task for task in tasks_dict}

        # projects_dict = [project.__dict__ for project in client.projects.list()]
        # project_name_to_id = {
        #     project["_model"]["name"]: project["_model"]["id"] for project in projects_dict
        # }
        read_annotations = 0
        for model_id, model in enumerate(params.models):
            if params.load:
                Model = functools.partial(LoadAnnotations, load_dir=params.load[model_id])
            elif params.ensemble.sfx:
                from cvataa.ensemble_cli import EnsembleCLI

                Model = EnsembleCLI

                sfx = params.ensemble.sfx
                model = f"ensemble" if sfx == "1" else f"ensemble_{sfx}"
                Model = functools.partial(
                    EnsembleCLI,
                    params=params.ensemble,
                    models=params.models,
                    name=model,
                    client=client,
                    task_name_to_obj=task_name_to_obj,
                )

            else:
                if model == "instanseg":
                    from instanseg_cli import InstansegCLI

                    Model = InstansegCLI
                elif model == "stardist":
                    from stardist_cli import StardistCLI

                    Model = StardistCLI
                elif model == "cellpose":
                    from cellpose_cli import CellposeCLI

                    Model = CellposeCLI
                elif "cellvit" in model:
                    from cellvit_cli import CellvitCLI

                    if model == "cellvit":
                        Model = CellvitCLI
                    elif model == "cellvit-hipt":
                        Model = functools.partial(CellvitCLI, model_type="hipt")
                    elif model == "cellvit-virchow":
                        Model = functools.partial(CellvitCLI, model_type="virchow")
                    else:
                        raise AssertionError(f"invalid cellvit model {model}")
                elif "microsam" in model:
                    read_annotations = 1

                    from microsam_cli import MicroSAMCLI

                    if model == "microsam":
                        Model = MicroSAMCLI
                    elif model == "microsam-l_lm":
                        Model = functools.partial(MicroSAMCLI, model_type="vit_l_lm")
                    elif model == "microsam-b_lm":
                        Model = functools.partial(MicroSAMCLI, model_type="vit_b_lm")
                    elif model == "microsam-t_lm":
                        Model = functools.partial(MicroSAMCLI, model_type="vit_t_lm")
                    elif model == "microsam-h_hist":
                        Model = functools.partial(MicroSAMCLI, model_type="vit_h_histopathology")
                    elif model == "microsam-l_hist":
                        Model = functools.partial(MicroSAMCLI, model_type="vit_l_histopathology")
                    elif model == "microsam-b_hist":
                        Model = functools.partial(MicroSAMCLI, model_type="vit_b_histopathology")
                    else:
                        raise AssertionError(f"invalid cellvit model {model}")

                    Model = MicroSAMCLI
                else:
                    raise AssertionError(f"invalid model {model}")

            task_suffix = "multi" if params.multi else model
            relevant_task_names = [
                task_name
                for task_name, task_id in task_name_to_id.items()
                if f"-{task_suffix}" in task_name
            ]

            relevant_task_names = params.filter.apply(relevant_task_names)

            assert relevant_task_names, "no relevant tasks found"

            relevant_task_names.sort()

            # task_name_to_obj = {
            #     task_name: task_name_to_obj[task_name] for task_name in relevant_task_names
            # }
            task_name_to_id = {
                task_name: task_name_to_obj[task_name]["_model"]["id"]
                for task_name in relevant_task_names
            }
            print(
                f"\nannotating {len(relevant_task_names)} tasks:\n{to_str(relevant_task_names)}\n"
            )

            n_tasks = len(relevant_task_names)
            for i, task_name in enumerate(relevant_task_names):

                if params.multi:
                    task_id = task_name_to_id[task_name]
                    task = client.tasks.retrieve(task_id)
                    labels = task.get_labels()
                    label_name_to_id = {label["name"]: i for i, label in enumerate(labels)}
                    label_id = label_name_to_id[model]

                frame_name_to_shapes = None
                if read_annotations:
                    frame_name_to_shapes, _ = get_cvat_annotations(
                        task_name, task_name_to_id, client
                    )

                n_frames = task_name_to_dict[task_name]["size"]
                func = Model(
                    task_name=task_name,
                    n_frames=n_frames,
                    frame_name_to_shapes=frame_name_to_shapes,
                    label_name=model if params.multi else "nucleus",
                    verbose=False,
                )
                print(f"\nannotating task {i+1} / {n_tasks}: {task_name}\n")
                try:
                    cvataa.annotate_task(
                        client,
                        task_name_to_id[task_name],
                        func,
                        clear_existing=True if (params.reset and not params.multi) else False,
                    )
                except datasets.common.UnsupportedDatasetError:
                    # empty dataset
                    pass

            if params.ensemble:
                break


if __name__ == "__main__":
    main()
