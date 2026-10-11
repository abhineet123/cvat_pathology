import os
import cv2
import numpy as np

np.set_printoptions(legacy="1.25")

from tqdm import tqdm
from PIL import Image
from datetime import datetime

import copy
import paramparse
import fiftyone as fo


from cvat_sdk import make_client
from cvat_sdk import masks

from cell_seg_utils import CVATAuth, Filter, linux_path, hex_to_rgb
from visualize_tasks import Params, run

# fo.close_app()
# print(fo.config)
# fo.config.default_app_port = 5252


class BatchParams(Params):
    """
    :ivar level: level at which to create each fiftyone dataset
        level=0: one dataset for each subdir
        level=1: one dataset for each model
        level=2: one dataset for each task
    """

    def __init__(self):
        Params.__init__(self)
        self.level = 0


def run_single(level, cvat_info, params: Params, dataset_name, **kwargs):
    run_parms: Params = copy.deepcopy(params)

    for arg_name, arg_val in kwargs.items():
        setattr(run_parms, arg_name, arg_val)

    dataset_suffixes = []
    if run_parms.chunk_id > 0:
        dataset_suffixes.append(f"chunk_{run_parms.chunk_id:02d}")

    if run_parms.grouped:
        dataset_suffixes.append(f"grouped")

    if run_parms.time_suffix:
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        dataset_suffixes.append(timestamp)

    if dataset_suffixes:
        dataset_suffix = "-".join(dataset_suffixes)
        dataset_name = f"{dataset_name}-{dataset_suffix}"

    run_parms.verbose = 0
    run_parms.dataset_name = dataset_name

    print(f"running level {level} job with dataset_name: {dataset_name}")
    run(run_parms, cvat_info)


def main():
    params: BatchParams = paramparse.process(BatchParams)

    dir_path = linux_path(params.root_dir, params.directory)
    if params.recursive:
        subdirs = [x[0] for x in os.walk(dir_path)]
    else:
        subdirs = [
            linux_path(dir_path, x)
            for x in os.listdir(dir_path)
            if os.path.isdir(linux_path(dir_path, x))
        ]

    try:
        subdirs.remove(dir_path)
    except ValueError:
        pass

    subdirs = params.filter.apply(subdirs)
    subdirs.sort()

    client_cfg = params.auth.to_cfg()

    n_subdirs = len(subdirs)
    assert n_subdirs, "no subdirs found"
    assert params.model_suffixes, "model_suffixes must be provided"

    base_dataset_name = f"{params.project_name}"
    model_suffixes = []
    for model_suffix in params.model_suffixes:
        if model_suffix == "multi":
            assert params.multi_labels, "multi_labels must be provided"
            labels_str = "_".join(params.multi_labels)
            model_suffixes.append(f"multi-{labels_str}")
        else:
            model_suffixes.append(model_suffix)

    if params.level == 0:
        models_suffix = "_".join(model_suffixes)
        base_dataset_name = f"{base_dataset_name}-{models_suffix}"

    if params.filter.iall:
        include_suffix = "_".join(params.filter.iall)
        base_dataset_name = f"{base_dataset_name}-{include_suffix}"

    client = make_client(**client_cfg)

    print("getting cvat tasks info...")
    tasks_dict = [task.__dict__ for task in client.tasks.list()]
    print("getting cvat projects info...")
    projects_dict = [project.__dict__ for project in client.projects.list()]

    cvat_info = (tasks_dict, projects_dict)

    task_name_to_obj = {task["_model"]["name"]: task for task in tasks_dict}
    relevant_task_names = list(task_name_to_obj.keys())
    relevant_task_names = params.filter.apply(relevant_task_names)

    assert relevant_task_names, "no relevant tasks found"

    relevant_task_names.sort()

    task_name_to_obj = {task_name: task_name_to_obj[task_name] for task_name in relevant_task_names}
    task_name_to_id = {
        task_name: task_name_to_obj[task_name]["_model"]["id"] for task_name in relevant_task_names
    }
    project_name_to_id = {
        project["_model"]["name"]: project["_model"]["id"] for project in projects_dict
    }

    args = dict(
        cvat_info=cvat_info,
        params=params,
    )

    for subdir_id, subdir in enumerate(subdirs):

        if subdir_id < params.start_dir_id:
            print(f"\nskipping subdir {subdir_id+1}/{n_subdirs}: {subdir}\n")
            continue

        if subdir_id > params.end_dir_id >= 0:
            print(f"\nskipping subdirs with id > {params.end_dir_id}\n")
            break

        subdir_name = os.path.basename(subdir)

        subdir_dataset_name = f"{base_dataset_name}-{subdir_name}"

        args.update(
            dict(
                start_dir_id=subdir_id,
                end_dir_id=subdir_id,
            )
        )
        if params.level == 0:
            print(f"\nsubdir {subdir_id+1}/{n_subdirs}: {subdir}\n")
            args.update(
                dict(
                    level=0,
                    dataset_name=subdir_dataset_name,
                )
            )

            if params.grouped == 2:
                run_single(**args, grouped=0)
                run_single(**args, grouped=1)
            else:
                run_single(**args)

            continue

        task_suffix = os.path.relpath(subdir, dir_path)
        n_model_suffixes = len(params.model_suffixes)
        for model_id, model_suffix in enumerate(params.model_suffixes):

            if model_id < params.start_model_id:
                print(f"\nskipping model {model_id+1}/{n_model_suffixes}: {model_suffix}\n")
                continue

            if model_id > params.end_model_id >= 0:
                print(f"\nskipping models with id > {params.end_model_id}\n")
                break

            model_dataset_name = f"{subdir_dataset_name}-{model_suffixes[model_id]}"

            args.update(
                dict(
                    start_model_id=model_id,
                    end_model_id=model_id,
                )
            )
            if params.level == 1:
                print(f"\nsubdir {subdir_id+1}/{n_subdirs}: {subdir}")
                print(f"\tmodel {model_id+1}/{n_model_suffixes}: {model_suffix}\n")
                args.update(
                    dict(
                        level=1,
                        dataset_name=model_dataset_name,
                    )
                )
                if params.grouped == 2:
                    run_single(**args, grouped=0)
                    run_single(**args, grouped=1)
                else:
                    run_single(**args)

                continue

            project_name = f"{params.project_name}-{model_suffix}"

            if project_name not in project_name_to_id:
                if params.ignore_invalid:
                    print(f"Skipping invalid project: {project_name}")
                    continue
                else:
                    raise AssertionError(f"invalid project_name: {project_name}")

            task_name_ = f"{project_name}-{task_suffix}"

            assert params.chunk_id == 0, "chunk_id must be 0 for level 2 batching"

            task_name_templ = f"{task_name_}-chunk_"
            task_names = [k for k in task_name_to_id.keys() if k.startswith(task_name_templ)]

            n_tasks = len(task_names)
            print(f"processing tasks for {n_tasks} chunks")

            for task_name_id, task_name in enumerate(task_names):
                if task_name_id < params.start_task_id:
                    print(f"\nskipping task {task_name_id+1}/{n_tasks}: {task_name}\n")
                    continue

                if task_name_id > params.end_task_id >= 0:
                    print(f"\nskipping tasks with id > {params.end_task_id}\n")
                    break

                task_dataset_name = model_dataset_name
                non_rep_task_suffixes = [
                    k for k in task_name.split("-") if k not in task_dataset_name
                ]
                if non_rep_task_suffixes:
                    non_rep_task_suffix = "-".join(non_rep_task_suffixes)
                    task_dataset_name = f"{task_dataset_name}-{non_rep_task_suffix}"

                args.update(
                    dict(
                        start_task_id=task_name_id,
                        end_task_id=task_name_id,
                    )
                )
                if params.level == 2:
                    print(f"\nsubdir {subdir_id+1}/{n_subdirs}: {subdir}")
                    print(f"\tmodel {model_id+1}/{n_model_suffixes}: {model_suffix}")
                    print(f"\ttask {task_name_id+1}/{n_tasks}: {task_name}\n")

                    args.update(
                        dict(
                            level=2,
                            dataset_name=task_dataset_name,
                        )
                    )
                    if params.grouped == 2:
                        run_single(**args, grouped=0)
                        run_single(**args, grouped=1)
                    else:
                        run_single(**args)

                    continue

    client.close()


if __name__ == "__main__":
    main()
