import numpy as np

np.set_printoptions(legacy="1.25")

import functools
import paramparse
from tqdm import tqdm

from cvat_sdk import make_client, datasets
from cvat_sdk.core import progress
import cvat_sdk.auto_annotation as cvataa

from cell_seg_utils import CVATAuth, Filter, LoadAnnotations, to_str, linux_path


class Params(paramparse.CFG):
    def __init__(self):
        paramparse.CFG.__init__(self)

        self.auth = CVATAuth()
        self.filter = Filter()

        self.models = []
        self.load = ""
        self.load_root = "/data/PDL1-2026-Tiles/vis"
        self.mask_dir_name = "masks-cellvit"
        self.reset = 1


def main():
    params: Params = paramparse.process(Params)

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
        projects_dict = [project.__dict__ for project in client.projects.list()]

        task_name_to_id = {task["_model"]["name"]: task["_model"]["id"] for task in tasks_dict}
        task_name_to_dict = {task["_model"]["name"]: task["_model"] for task in tasks_dict}
        project_name_to_id = {
            project["_model"]["name"]: project["_model"]["id"] for project in projects_dict
        }
        for model_id, model in enumerate(params.models):
            if params.load:
                Model = functools.partial(LoadAnnotations, load_dir=params.load[model_id])
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
                elif model == "ensemble":
                    from cell_seg_ensemble import CellSegEnsembleCLI

                    Model = CellSegEnsembleCLI
                else:
                    raise AssertionError(f"invalid model {model}")

            relevant_task_names = [
                task_name
                for task_name, task_id in task_name_to_id.items()
                if f"-{model}" in task_name
            ]

            relevant_task_names = params.filter.apply(relevant_task_names)

            assert relevant_task_names, "no relevant tasks found"

            relevant_task_names.sort()

            print(
                f"\nannotating {len(relevant_task_names)} tasks:\n{to_str(relevant_task_names)}\n"
            )

            n_tasks = len(relevant_task_names)
            for i, task_name in enumerate(relevant_task_names):
                n_frames = task_name_to_dict[task_name]["size"]
                func = Model(task_name=task_name, n_frames=n_frames, verbose=False)
                print(f"\nannotating task {i+1} / {n_tasks}: {task_name}\n")
                # pbar = progress.BaseProgressReporter()
                try:
                    cvataa.annotate_task(
                        client,
                        task_name_to_id[task_name],
                        func,
                        clear_existing=True if params.reset else False,
                        # pbar=pbar,
                    )
                except datasets.common.UnsupportedDatasetError:
                    # empty dataset
                    pass


if __name__ == "__main__":
    main()
