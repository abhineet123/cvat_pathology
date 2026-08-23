import os
import time
import sys
import numpy as np

# np.set_printoptions(legacy="1.25")

import functools
import paramparse
from tqdm import tqdm

from cvat_sdk import make_client, datasets, api_client
import cvat_sdk.auto_annotation as cvataa

# from cvat_sdk.core import progress

from cell_seg_utils import (
    CVATAuth,
    Filter,
    to_str,
    linux_path,
    sleep_with_pbar,
)

from cell_seg_params import EnsembleParams


class Params(paramparse.CFG):
    def __init__(self):
        paramparse.CFG.__init__(self)

        self.auth = CVATAuth()
        self.filter = Filter()

        self.models = []
        self.load = []
        self.load_root = "/data/PDL1-2026-Tiles/vis"
        self.mask_dir_name = "masks-cellvit"
        self.multi = 0
        self.reset = 1
        self.delete_ann = 0
        self.delete_task = 0
        self.start_id = 0
        self.end_id = -1
        self.excp_wait_t = 120

        self.ensemble = EnsembleParams()


def get_model_cli(model_name: str, model_id: int, params: Params):
    if model_name == "instanseg":
        from instanseg_cli import InstansegCLI

        ModelCLI = InstansegCLI
    elif model_name == "stardist":
        from stardist_cli import StardistCLI

        ModelCLI = StardistCLI
    elif model_name == "cellpose":
        from cellpose_cli import CellposeCLI

        ModelCLI = CellposeCLI
    elif "cellvit" in model_name:
        from cellvit_cli import CellvitCLI

        if model_name == "cellvit":
            ModelCLI = CellvitCLI
        elif model_name == "cellvit-hipt":
            ModelCLI = functools.partial(CellvitCLI, model_type="hipt")
        elif model_name == "cellvit-virchow":
            ModelCLI = functools.partial(CellvitCLI, model_type="virchow")
        else:
            raise AssertionError(f"invalid cellvit model {model_name}")
    elif "microsam" in model_name:
        from microsam_cli import MicroSAMCLI

        if model_name == "microsam":
            ModelCLI = MicroSAMCLI
        elif model_name == "microsam-l_lm":
            ModelCLI = functools.partial(MicroSAMCLI, model_type="vit_l_lm")
        elif model_name == "microsam-b_lm":
            ModelCLI = functools.partial(MicroSAMCLI, model_type="vit_b_lm")
        elif model_name == "microsam-t_lm":
            ModelCLI = functools.partial(MicroSAMCLI, model_type="vit_t_lm")
        elif model_name == "microsam-h_hist":
            ModelCLI = functools.partial(MicroSAMCLI, model_type="vit_h_histopathology")
        elif model_name == "microsam-l_hist":
            ModelCLI = functools.partial(MicroSAMCLI, model_type="vit_l_histopathology")
        elif model_name == "microsam-b_hist":
            ModelCLI = functools.partial(MicroSAMCLI, model_type="vit_b_histopathology")
        else:
            raise AssertionError(f"invalid cellvit model {model_name}")

        ModelCLI = MicroSAMCLI
    elif model_name.startswith("load-"):
        from load_cli import LoadAnnotations

        ModelCLI = functools.partial(LoadAnnotations, load_dir=params.load[model_id])
    elif model_name.startswith("ensemble"):
        from cvataa.ensemble_cli import EnsembleCLI

        ModelCLI = functools.partial(
            EnsembleCLI,
            params=params.ensemble,
            models=params.models,
            name=model_name,
        )
    else:
        raise AssertionError(f"invalid model: {model_name}")

    return ModelCLI


def main():
    params: Params = paramparse.process(Params)

    cvat_path = linux_path(os.path.expanduser("~"), "cvat_pathology")
    sys.path.append(cvat_path)

    client_cfg = params.auth.to_cfg()

    if params.load:
        params.load = ",".split(params.load)
        assert len(params.load) == len(params.models), "load - models len mismatch"

        if params.load_root:
            params.load = [linux_path(params.load_root, k) for k in params.load]
        if params.mask_dir_name:
            params.load = [linux_path(k, params.mask_dir_name) for k in params.load]

    client = make_client(**client_cfg)

    print("getting cvat tasks info...")
    tasks_dict = [task.__dict__ for task in client.tasks.list()]
    task_name_to_id = {task["_model"]["name"]: task["_model"]["id"] for task in tasks_dict}
    task_name_to_dict = {task["_model"]["name"]: task["_model"] for task in tasks_dict}
    task_name_to_obj = {task["_model"]["name"]: task for task in tasks_dict}

    # projects_dict = [project.__dict__ for project in client.projects.list()]
    # project_name_to_id = {
    #     project["_model"]["name"]: project["_model"]["id"] for project in projects_dict
    # }

    skip_annotating = False

    sfx = params.ensemble.sfx
    if sfx:
        ensemble_name = f"ensemble" if sfx == "1" else f"ensemble_{sfx}"
        models = [
            ensemble_name,
        ]
        skip_annotating = (
            params.ensemble.dups == 2
            or params.ensemble.meta.cvat == 2
            or params.ensemble.meta.fo == 2
        )
    else:
        models = params.models

    if params.load:
        models = [f"load-{model}" for model in models]

    for model_id, model in enumerate(models):
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

        n_tasks = len(relevant_task_names)

        print(f"\nannotating {n_tasks} tasks:\n{to_str(relevant_task_names)}\n")

        ModelCLI = get_model_cli(model, model_id, params)

        i = 0
        while i < n_tasks:

            if i > params.end_id >= 0:
                break

            task_name = relevant_task_names[i]

            if i < params.start_id:
                print(f"\n\nskipping task {i+1} / {n_tasks}: {task_name}")
                i += 1
                continue

            task_id = task_name_to_id[task_name]
            task = client.tasks.retrieve(task_id)

            if params.delete_task:
                print(f"\ndeleting task {i+1} / {n_tasks}: {task_name}")
                task.remove()
                i += 1
                continue

            if params.delete_ann:
                print(f"\ndeleting existing annotations for task {i+1} / {n_tasks}: {task_name}")
                task.remove_annotations()
                if params.delete == 2:
                    i += 1
                    continue

            print(f"\n\nannotating task {i+1} / {n_tasks}: {task_name}")

            # labels = task.get_labels()
            # if params.multi:
            #     label_name_to_id = {label["name"]: i for i, label in enumerate(labels)}
            #     label_id = label_name_to_id[model]

            n_frames = task_name_to_dict[task_name]["size"]
            func = ModelCLI(
                task_name=task_name,
                client=client,
                task_name_to_obj=task_name_to_obj,
                label_name=model if params.multi else "nucleus",
                n_frames=n_frames,
                verbose=False,
            )

            if skip_annotating:
                i += 1
                continue

            try:
                cvataa.annotate_task(
                    client,
                    task_name_to_id[task_name],
                    func,
                    clear_existing=True if (params.reset and not params.multi) else False,
                )
            except (
                api_client.exceptions.ServiceException,
                FileNotFoundError,
            ) as e:
                # wait a few seconds and try again to hopefully find cvat server responsive
                print(
                    f"\n\nTask annotation failed:\n{e}\nWaiting {params.excp_wait_t} seconds before trying again\n\n"
                )
                sleep_with_pbar(params.excp_wait_t)
                continue
            except datasets.common.UnsupportedDatasetError as e:
                # empty dataset
                print(f"\n\nfound invalid empty dataset:\n{e}\n\n")

            i += 1

        if params.ensemble.sfx:
            break

    client.close()


if __name__ == "__main__":
    main()
