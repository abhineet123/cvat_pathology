import os
import paramparse

from tqdm import tqdm
from datetime import datetime

from cvat_sdk import make_client, models
from cvat_sdk.core.proxies.tasks import ResourceType, Task

from cell_seg_utils import CVATAuth, Filter, to_str

from pprint import pprint

from cvat_sdk.api_client import Configuration, ApiClient, exceptions, models


class Params(paramparse.CFG):
    def __init__(self):
        paramparse.CFG.__init__(self)

        self.auth = CVATAuth()
        self.filter = Filter()

        self.root_dir = "/data/PDL1-2026-Tiles"
        self.directory = ""
        self.recursive = 0

        self.project_name = ""

        self.model_suffixes = []
        self.max_images = 0

        # self.model_suffix = "stardist"
        # self.model_suffix = "instanseg"
        # self.model_suffix = "ensemble"


def linux_path(*args, **kwargs):
    return os.path.join(*args, **kwargs).replace(os.sep, "/")


def create_project_lla(cfg_dict, name):
    configuration = Configuration(**cfg_dict)
    with ApiClient(configuration) as api_client:
        project_write_request = models.ProjectWriteRequest(
            name=name,
            labels=[
                models.PatchedLabelRequest(
                    id=1,
                    name="nucleus",
                    color="#fafa37",
                    type="any",
                ),
            ],
        )
        try:
            (data, response) = api_client.projects_api.create(
                project_write_request,
                # x_organization=x_organization,
                # org=org,
                # org_id=org_id,
            )
            return data
        except exceptions.ApiException as e:
            print("Exception when calling ProjectsApi.create(): %s\n" % e)


def create_project_hla(api_client, name):
    project_spec = dict(
        name=name,
        labels=[
            dict(
                name="nucleus",
                color="#fafa37",
                type="any",
            )
        ],
    )
    try:
        project = api_client.projects.create(
            project_spec,
        )
        pprint(project)
    except exceptions.ApiException as e:
        print("Exception when calling projects.create(): %s\n" % e)


def get_projects(client):
    projects_dict = [project.__dict__ for project in client.projects.list()]
    project_name_to_id = {
        project["_model"]["name"]: project["_model"]["id"] for project in projects_dict
    }
    project_name_to_dict = {
        project["_model"]["name"]: project["_model"] for project in projects_dict
    }
    return projects_dict, project_name_to_id, project_name_to_dict


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    https://stackoverflow.com/a/312464
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


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

    with make_client(**client_cfg) as client:
        for model_suffix in params.model_suffixes:
            project_name = f"{params.project_name}"
            if model_suffix:
                project_name = f"{project_name}-{model_suffix}"
            projects_dict, project_name_to_id, project_name_to_dict = get_projects(client)

            tasks_dict = [task.__dict__ for task in client.tasks.list()]
            task_name_to_id = {task["_model"]["name"]: task["_model"]["id"] for task in tasks_dict}

            if project_name not in project_name_to_id:
                # raise AssertionError(f"invalid project_name: {project_name}")
                timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
                print(f"{timestamp} creating project: {project_name}")

                project_dict = create_project_lla(client_cfg, project_name)
                project_id = project_dict["id"]

                projects_dict, project_name_to_id, project_name_to_dict = get_projects(client)

                assert project_id == project_name_to_id[project_name]

            # tasks_meta = [task.get_meta().to_dict() for task in tasks]
            # projects_preview = [project.get_preview() for project in projects]

            project_id = project_name_to_id[project_name]
            project_dict = project_name_to_dict[project_name]

            n_subdirs = len(subdirs)

            assert n_subdirs, "no subdirs found"
            image_exts = ["jpg", "jpeg", "bmp", "png", "tif", "webp"]

            for subdir_id, subdir in enumerate(subdirs):
                task_name = os.path.relpath(subdir, dir_path)
                task_name = f"{project_name}-{task_name}"

                # if model_suffix:
                # task_name = f"{task_name}-{model_suffix}"

                if task_name in task_name_to_id:
                    print(f"{subdir_id+1} / {n_subdirs} skipping existing task: {task_name}")
                    continue

                image_paths = [
                    os.path.join(subdir, k)
                    for k in os.listdir(subdir)
                    if any(k.lower().endswith(f".{_ext}") for _ext in image_exts)
                ]

                if not image_paths:
                    print(f"Skipping subdir with no images: {subdir}")
                    continue

                n_images = len(image_paths)
                timestamp = datetime.now().strftime("%y%m%d_%H%M%S")

                print(
                    f"{timestamp} creating task for subdir {subdir_id+1} / {n_subdirs} with {n_images} images: {task_name}"
                )

                if params.max_images > 0 and n_images > params.max_images:
                    image_paths_chunks = list(chunks(image_paths, params.max_images))
                    n_chunks = len(image_paths_chunks)
                    print(
                        f"splitting {n_images} images into {n_chunks} chunks of size <= {params.max_images}"
                    )

                    for chunk_id, image_paths_chunk in enumerate(image_paths_chunks):
                        n_chunk_images = len(image_paths_chunk)
                        task_spec = {
                            "name": f"{task_name}-{chunk_id}",
                            "project_id": project_id,
                        }
                        print(
                            f"\tchunk {chunk_id+1} / {n_chunks} with {n_chunk_images} images: {task_spec['name']}"
                        )
                        task = client.tasks.create_from_data(
                            spec=task_spec,
                            resource_type=ResourceType.LOCAL,
                            resources=image_paths_chunk,
                        )
                        assert task.size == n_chunk_images

                else:
                    task_spec = {
                        "name": task_name,
                        "project_id": project_id,
                    }
                    task = client.tasks.create_from_data(
                        spec=task_spec,
                        resource_type=ResourceType.LOCAL,
                        resources=image_paths,
                    )
                    assert task.size == n_images

                # return


if __name__ == "__main__":
    main()
