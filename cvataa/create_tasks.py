import os
import time
from tqdm import tqdm
from datetime import datetime

import paramparse

from cvat_sdk import make_client
from cvat_sdk.core.proxies.tasks import ResourceType
from cvat_sdk.api_client import exceptions

from cell_seg_utils import (
    CVATAuth,
    Filter,
    to_str,
    sleep_with_pbar,
    linux_path,
    create_project_lla,
    get_cvat_tasks_hla,
    delete_cvat_task_hla,
    get_cvat_projects_hla,
    chunks,
)


class Params(paramparse.CFG):
    class Chunk:
        def __init__(self):
            self.count = 0
            self.size = 0
            self.tolerance = 0

    def __init__(self):
        paramparse.CFG.__init__(self)

        self.auth = CVATAuth()
        self.filter = Filter()

        self.root_dir = "/data/PDL1-2026-Tiles"
        self.directory = ""
        self.recursive = 0
        self.multi = 0

        self.start_dir_id = 0
        self.end_dir_id = -1
        self.excp_wait_t = 120

        self.project_name = ""

        self.chunk = Params.Chunk()

        self.model_suffixes = []

        # self.model_suffix = "stardist"
        # self.model_suffix = "instanseg"
        # self.model_suffix = "ensemble"

        self.label_cols = [
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#f1a66d",
            "#e12AFB",
            "#00ffff",
        ]


def create_cvat_project(client, client_cfg, project_name, label_names, label_cols):
    print("get_projects...")
    projects_dict, project_name_to_id, project_name_to_dict = get_cvat_projects_hla(client)

    if project_name not in project_name_to_id:
        # raise AssertionError(f"Nonexistent project: {project_name}")
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        print(f"{timestamp} creating project: {project_name}")

        project_dict = create_project_lla(
            client_cfg,
            project_name,
            label_names=label_names,
            label_cols=label_cols,
        )

        project_id = project_dict["id"]

        projects_dict, project_name_to_id, project_name_to_dict = get_cvat_projects_hla(client)

        assert project_id == project_name_to_id[project_name]

    # tasks_meta = [task.get_meta().to_dict() for task in tasks]
    # projects_preview = [project.get_preview() for project in projects]

    project_id = project_name_to_id[project_name]

    # project_dict = project_name_to_dict[project_name].to_dict()
    # project_tasks = project_dict["tasks"]

    return project_id


def main():
    params: Params = paramparse.process(Params)

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

    assert subdirs, "no subdirs found"

    subdirs.sort()

    print(f"\ncreating tasks from {len(subdirs)} subdirs:\n{to_str(subdirs)}\n")

    if not params.model_suffixes:
        params.model_suffixes = [""]

    client_cfg = params.auth.to_cfg()

    project_suffixes = (
        params.model_suffixes
        if not params.multi
        else [
            "multi",
        ]
    )

    with make_client(**client_cfg) as client:

        for project_suffix in project_suffixes:
            project_name = f"{params.project_name}"
            if project_suffix:
                project_name = f"{project_name}-{project_suffix}"

            project_id = create_cvat_project(
                client,
                client_cfg,
                project_name,
                label_names=params.model_suffixes if params.multi else None,
                label_cols=params.label_cols,
            )
            task_name_to_id = get_cvat_tasks_hla(client)

            n_subdirs = len(subdirs)

            assert n_subdirs, "no subdirs found"
            image_exts = ["jpg", "jpeg", "bmp", "png", "tif", "webp"]

            subdir_id = 0

            while subdir_id < n_subdirs:
                subdir = subdirs[subdir_id]
                task_name = os.path.relpath(subdir, dir_path)
                task_name = f"{project_name}-{task_name}"

                if subdir_id < params.start_dir_id:
                    print(f"{subdir_id+1} / {n_subdirs} skipping task: {task_name}")
                    subdir_id += 1
                    continue

                if subdir_id > params.end_dir_id >= 0:
                    break

                if task_name in task_name_to_id:
                    print(f"{subdir_id+1} / {n_subdirs} skipping existing task: {task_name}")
                    subdir_id += 1
                    continue

                image_paths = [
                    os.path.join(subdir, k)
                    for k in os.listdir(subdir)
                    if any(k.lower().endswith(f".{_ext}") for _ext in image_exts)
                ]

                if not image_paths:
                    print(f"Skipping subdir with no images: {subdir}")
                    subdir_id += 1
                    continue

                n_images = len(image_paths)
                timestamp = datetime.now().strftime("%y%m%d_%H%M%S")

                print(
                    f"{timestamp} creating task for subdir {subdir_id+1} / {n_subdirs} with {n_images} images: {task_name}"
                )

                if params.chunk.size > 0 and n_images > params.chunk.size:
                    image_paths_chunks = list(chunks(image_paths, params.chunk.size))

                    """if the last chunk is too small, subsume it within the second last chunk"""

                    if len(image_paths_chunks[-1]) < int(
                        params.chunk.tolerance * params.chunk.size
                    ):
                        image_paths_chunks[-2] += image_paths_chunks[-1]
                        del image_paths_chunks[-1]

                    n_chunks = len(image_paths_chunks)

                    if n_chunks >= params.chunk.count > 0:
                        n_chunks = params.chunk.count

                    print(
                        f"splitting {n_images} images into {n_chunks} chunks of size <= {params.chunk.size} (tolerance: {params.chunk.tolerance})"
                    )

                    chunk_id = 0
                    while chunk_id < n_chunks:
                        image_paths_chunk = image_paths_chunks[chunk_id]
                        chunk_task_name = f"{task_name}-chunk_{chunk_id+1:02d}"
                        if chunk_task_name in task_name_to_id:
                            print(
                                f"\tchunk {chunk_id+1} / {n_chunks} skipping existing task: {chunk_task_name}"
                            )
                            chunk_id += 1
                            continue

                        n_chunk_images = len(image_paths_chunk)
                        task_spec = {
                            "name": chunk_task_name,
                            "project_id": project_id,
                        }
                        print(
                            f"\tchunk {chunk_id+1} / {n_chunks} with {n_chunk_images} images: {task_spec['name']}"
                        )
                        try:
                            task = client.tasks.create_from_data(
                                spec=task_spec,
                                resource_type=ResourceType.LOCAL,
                                resources=image_paths_chunk,
                                # pbar=TQDMProgressReporter(),
                            )
                        except exceptions.ServiceException as e:
                            print(
                                f"\n\nTask creation failed:\n{e}\nWaiting {params.excp_wait_t} seconds before trying again\n\n"
                            )
                            sleep_with_pbar(params.excp_wait_t)
                            task_name_to_id = delete_cvat_task_hla(client, chunk_task_name)
                            continue
                        else:
                            assert task.size == n_chunk_images
                            chunk_id += 1

                else:
                    task_spec = {
                        "name": task_name,
                        "project_id": project_id,
                    }
                    try:
                        task = client.tasks.create_from_data(
                            spec=task_spec,
                            resource_type=ResourceType.LOCAL,
                            resources=image_paths,
                            # pbar=TQDMProgressReporter(),
                        )
                    except exceptions.ServiceException as e:
                        print(
                            f"\n\nTask creation failed:\n{e}\nWaiting {params.excp_wait_t} seconds before trying again\n\n"
                        )
                        sleep_with_pbar(params.excp_wait_t)
                        task_name_to_id = delete_cvat_task_hla(client, task_name)
                        continue
                    else:
                        assert task.size == n_images

                subdir_id += 1

                # return


if __name__ == "__main__":
    main()
