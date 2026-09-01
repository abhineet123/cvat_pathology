import os
import time
import cv2
from pprint import pprint
import itertools
import compress_json
import geojson
import gzip
import math
import json
import shapely
from datetime import datetime

import numpy as np
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
from skimage.measure import approximate_polygon, find_contours

from cvat_sdk.core.progress import ProgressReporter
from cvat_sdk.api_client import Configuration, ApiClient, exceptions, models
from cvat_sdk import make_client
from cvat_sdk import Client
from cvat_sdk.core.proxies.tasks import Task

from cell_seg_params import EnsembleParams

label_map_info = {
    "binary": {
        # "Tumor"
        # "Non-Tumor"
        "ternary": {
            "Tumor": "Tumor",
            "Stroma": "Non-Tumor",
            "Immune cells": "Non-Tumor",
        },
        "pannuke": {
            "Neoplastic": "Tumor",
            "Epithelial": "Non-Tumor",
            "Inflammatory": "Non-Tumor",
            "Connective": "Non-Tumor",
            "Dead": "Non-Tumor",
        },
        "nucls_main": {
            "Tumor": "Tumor",
            "Mitotic": "Tumor",
            "Stromal": "Non-Tumor",
            "Macrophage": "Non-Tumor",
            "Lymphocyte": "Non-Tumor",
            "Plasma": "Non-Tumor",
            "Other": "Non-Tumor",
        },
        "nucls_super": {
            "Tumor": "Tumor",
            "Stromal": "Non-Tumor",
            "sTILs": "Non-Tumor",
            "Other": "Non-Tumor",
        },
        "ocelot": {
            "Tumor Cell": "Tumor",
            "Other Cell": "Non-Tumor",
        },
    },
    "ternary": {
        # "Tumor"
        # "Stroma"
        # "Immune cells"
        # "Other"
        "pannuke": {
            "Neoplastic": "Tumor",
            "Epithelial": "Other",
            "Inflammatory": "Immune cells",
            "Connective": "Stroma",
            "Dead": "Other",
        },
        "nucls_main": {
            "Tumor": "Tumor",
            "Mitotic": "Tumor",
            "Stromal": "Stroma",
            "Macrophage": "Stroma",
            "Lymphocyte": "Immune cells",
            "Plasma": "Immune cells",
            "Other": "Other",
        },
        "nucls_super": {
            "Tumor": "Tumor",
            "Stromal": "Stroma",
            "sTILs": "Immune cells",
            "Other": "Other",
        },
        "consep": {
            "Inflammatory": "Immune cells",
            "Epithelial": "Tumor",
            "Spindle-Shaped": "Stroma",
            "Other": "Other",
        },
        "lizard": {
            "Neutrophil": "Other",
            "Epithelial": "Tumor",
            "Lymphocyte": "Immune cells",
            "Plasma": "Immune cells",
            "Eosinophil": "Other",
            "Connective tissue": "Stroma",
        },
        "panoptils": {
            "Epithelial Cells": "Tumor",
            "Stromal Cells": "Stroma",
            "TILs": "Immune cells",
            "Other Cells": "Other",
        },
    },
}
label_set_info = {
    "seg_only": {
        "nucleus": "#009900",
    },
    "binary": {
        "Tumor": "#ff0000",
        "Non-Tumor": "#00ff00",
    },
    "qupath": {
        "Tumor": "#ff0000",
        "Stroma": "#00ff00",
        "Immune cells": "#0000ff",
        "Other": "#ffff00",
    },
    "pannuke": {
        "Neoplastic": "#ff0000",
        "Epithelial": "#ffa500",
        "Inflammatory": "#00ff00",
        "Connective": "#0000ff",
        "Dead": "#ffff00",
    },
    "nucls_main": {
        "Tumor": "#ff0000",
        "Mitotic": "#ff00ff",
        "Stromal": "#228b22",
        "Macrophage": "#00ff00",
        "Lymphocyte": "#0000ff",
        "Plasma": "#00ffff",
        "Other": "#ffff00",
    },
    "nucls_super": {
        "Tumor": "#ff0000",
        "Stromal": "#228b22",
        "sTILs": "#0000ff",
        "Other": "#ffff00",
    },
    "ocelot": {
        "Tumor Cell": "#ff0000",
        "Other Cell": "#228b22",
    },
    "consep": {
        "Inflammatory": "#228b22",
        "Epithelial": "#ffa500",
        "Spindle-Shaped": "#0000ff",
        "Other": "#ffff00",
    },
    "lizard": {
        "Neutrophil": "#ff0000",
        "Epithelial": "#ffa500",
        "Lymphocyte": "#ffff00",
        "Plasma": "#00ffff",
        "Eosinophil": "#ff00ff",
        "Connective tissue": "#0000ff",
    },
    "panoptils": {
        "Epithelial Cells": "#ffa500",
        "Stromal Cells": "#228b22",
        "TILs": "#ff0000",
        "Other Cells": "#ffff00",
    },
    "midog": {
        "Mitotic": "#ff0000",
        "Non-Mitotic": "#228b22",
    },
}

COLOR_DICT_CELLS = {
    "cell": [0, 255, 0],
    "nucleus": [0, 255, 0],
    "Tumor": [255, 0, 0],
    "Tumor Cell": [255, 0, 0],
    "Inflammatory": [255, 0, 0],
    "Stroma": [150, 200, 150],
    "Stromal": [150, 200, 150],
    "sTILs": [34, 221, 77],
    "Other": [255, 200, 0],
    "Other Cell": [255, 200, 0],
    "Mitotic": [255, 159, 68],
    "Macrophage": [80, 56, 112],
    "Lymphocyte": [87, 112, 56],
    "Plasma": [110, 0, 0],
    "Neoplastic": [255, 196, 196],
    "Connective": [214, 255, 196],
    "Dead": [255, 0, 255],
    "Epithelial": [0, 255, 255],
    "tile": [0, 0, 0],
    "roi": [255, 0, 0],
}


class TQDMProgressReporter(ProgressReporter):
    def start2(
        self,
        total: int,
        *,
        desc: str | None = None,
        unit: str = "it",
        unit_scale: bool = False,
        unit_divisor: int = 1000,
        **kwargs,
    ) -> None:
        """
        Initializes the progress bar.

        total, desc, unit, unit_scale, unit_divisor have the same meaning as in tqdm.

        kwargs is included for future extension; implementations of this method
        must ignore it.
        """
        self.pbar = tqdm(total=total, desc=desc)

    def report_status(self, progress: int):
        """Updates the progress bar"""
        self.pbar.update(progress)

    def advance(self, delta: int):
        """Updates the progress bar"""
        self.pbar.update(delta)

    def finish(self):
        """Finishes the progress bar"""
        self.pbar.close()


class Filter:
    """
    :ivar iall: list of strings that must all be contained in an item for it to be included
    :ivar iany: list of strings out of which at least one must be contained in an item for it to be included
    :ivar eall: list of strings that must all be contained in an item for it to be excluded
    :ivar eany: list of strings out of which at least one must be contained in an item for it to be excluded
    """

    def __init__(self):
        self.iall = []
        self.iany = []
        self.eall = []
        self.eany = []

        self.start_id = 0
        self.end_id = -1

        self.sort_by_id = 0

    def apply(self, relevant_task_names):
        if self.iall:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if all(str(k) in task_name for k in self.iall)
            ]
            relevant_task_names.sort(key=path_to_id if self.sort_by_id else path_to_name)

        if self.iany:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if any(str(k) in task_name for k in self.iany)
            ]
            relevant_task_names.sort(key=path_to_id if self.sort_by_id else path_to_name)

        if self.eall:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if not all(str(k) in task_name for k in self.eall)
            ]
            relevant_task_names.sort(key=path_to_id if self.sort_by_id else path_to_name)

        if self.eany:
            relevant_task_names = [
                task_name
                for task_name in relevant_task_names
                if not any(str(k) in task_name for k in self.eany)
            ]
            relevant_task_names.sort(key=path_to_id if self.sort_by_id else path_to_name)

        relevant_task_names.sort(key=path_to_id if self.sort_by_id else path_to_name)

        # print(f"all wsi_files:\n {to_str(relevant_task_names)}")

        relevant_task_names = self.apply_ids(relevant_task_names)

        return relevant_task_names

    def apply_ids(self, relevant_task_names, ids=None, suffix=False):
        if ids is None:
            start_id, end_id = self.start_id, self.end_id
        else:
            start_id, end_id = ids

        if relevant_task_names and (start_id > 0 or end_id >= start_id):
            if end_id < start_id:
                end_id = len(relevant_task_names) - 1

            relevant_task_names = relevant_task_names[start_id : end_id + 1]

            if suffix:
                return relevant_task_names, f"{start_id}_{end_id}"

        if suffix:
            return relevant_task_names, ""

        return relevant_task_names


class CVATAuth:
    def __init__(self):
        self.host = ""
        self.access_token = ""
        self.username = ""
        self.pwd = ""

    def to_cfg(self):
        if not self.host:
            try:
                self.host = os.environ["CVAT_HOST"]
            except KeyError:
                raise AssertionError("cvat host must be provided")

        if not self.access_token:
            try:
                self.access_token = os.environ["CVAT_ACCESS_TOKEN"]
            except KeyError:
                if not self.username and not self.pwd:
                    try:
                        self.username = os.environ["CVAT_USERNAME"]
                        self.pwd = os.environ["CVAT_PWD"]
                    except KeyError:
                        raise AssertionError(
                            "either cvat access_token or username / pwd must be provided"
                        )

        client_cfg = dict(host=self.host)
        if self.access_token:
            client_cfg.update(dict(access_token=self.access_token))
        else:
            client_cfg.update(dict(credentials=(self.username, self.pwd)))

        return client_cfg


def delete_issues(client, frame_id, job_id):
    issue_list, _ = client.api_client.issues_api.list(
        frame_id=frame_id,
        job_id=job_id,
    )
    issue_list = issue_list.to_dict()
    issue_ids = [issue["id"] for issue in issue_list["results"]]

    if issue_ids:
        # print("deleting existing issues")
        for issue_id in issue_ids:
            client.api_client.issues_api.destroy(
                issue_id,
            )
        issue_list, _ = client.api_client.issues_api.list(
            frame_id=frame_id,
            job_id=job_id,
        )
        issue_list = issue_list.to_dict()
        issue_ids = [issue["id"] for issue in issue_list["results"]]

        assert not issue_ids, "non empty issue_ids even after deletion"


def add_issue(cvat_client: Client, frame_id, job_id, message):
    cvat_client.issues.create(
        dict(
            frame=frame_id,
            position=[
                0.0,
            ],
            job=job_id,
            # assignee=user_id,
            message=message,
            # owner=dict(id=2),
            resolved=True,
        )
    )


def add_frame_metadata(
    params: EnsembleParams.Metadata,
    client: Client,
    job_id,
    task_id,
    task_name,
    name,
    frame_name_to_info,
    model_to_shapes,
):
    # comments = self.client.comments.list()
    # users = self.client.users.list()
    # usernames_to_id = {user._model["username"]: user._model["id"] for user in users}
    # print()

    if params.cvat:
        cvat_client = make_client(
            host=client.api_map.host,
            access_token=os.environ["CVAT_ACCESS_TOKEN_CVAT"],
        )

    if params.fo:
        fiftyone_client_ovl = make_client(
            host=client.api_map.host,
            access_token=os.environ["CVAT_ACCESS_TOKEN_51_OVL"],
        )
        fiftyone_client_sep = make_client(
            host=client.api_map.host,
            access_token=os.environ["CVAT_ACCESS_TOKEN_51_SEP"],
        )
        filename_to_51_url_sep, fo_db_url = read_51_metadata(
            params.fo_root, task_name, name, grouped=1, db_url=1
        )
        request_body = models.PatchedTaskWriteRequest(name=task_name, bug_tracker=fo_db_url)
        # request_body = models.TaskWriteRequest(name="fo_url", bug_tracker=fo_db_url)
        client.api_client.tasks_api.partial_update(
            id=task_id,
            patched_task_write_request=request_body,
            # task_write_request=request_body,
        )
        filename_to_51_url_ovl = read_51_metadata(params.fo_root, task_name, name, grouped=0)

    for frame_name, frame_info in tqdm(frame_name_to_info.items(), "adding metadata to frames"):
        frame_id = int(frame_info["id"])

        if params.reset:
            delete_issues(client, frame_id, job_id)

        if params.cvat:
            frame_shapes = [
                frame_name_to_shapes[frame_name]
                for _, frame_name_to_shapes in model_to_shapes.items()
            ]
            frame_shapes = [x for xs in frame_shapes for x in xs]
            frame_urls = set(shape["frame_url"] for shape in frame_shapes)
            for frame_url in frame_urls:
                add_issue(cvat_client, frame_id, job_id, f"{frame_url}")

        if params.fo:
            add_issue(
                fiftyone_client_sep, frame_id, job_id, f"{filename_to_51_url_sep[frame_name]}"
            )
            add_issue(
                fiftyone_client_ovl, frame_id, job_id, f"{filename_to_51_url_ovl[frame_name]}"
            )

    if params.fo:
        fiftyone_client_ovl.close()
        fiftyone_client_sep.close()

    if params.cvat:
        cvat_client.close()


def find_duplicate_shapes(model_to_shapes, remove):
    print("\nchecking for duplicates...")
    for model, frame_name_to_shapes in model_to_shapes.items():
        for frame_name, shapes in tqdm(frame_name_to_shapes.items(), desc=model):
            pts_all = [tuple(shape["points"]) for shape in shapes]

            unique_pts = set()
            unique_pts_ids = set()
            duplicate_pts_ids = [
                pts_id
                for pts_id, pts in enumerate(pts_all)
                if pts in unique_pts or (unique_pts.add(pts) and unique_pts_ids.add(pts_id))
            ]
            if duplicate_pts_ids:
                print(f"{model} : {frame_name} :: found {len(duplicate_pts_ids)} duplicate shapes")
                if remove:
                    frame_name_to_shapes[frame_name] = [
                        shapes[unique_pts_id] for unique_pts_id in unique_pts_ids
                    ]
                else:
                    raise AssertionError("duplicate shapes are not allowed")

    # print("\nno duplicates found")


def get_51_url(grouped):
    base_env_name = "FIFTYONE_HOST"
    env_name = f'{base_env_name}_{"SEP" if grouped else "OVL"}'
    try:
        host_url = os.environ[env_name]
    except KeyError:
        # print(f"env {env_name} not found so falling back to {base_env_name}")
        try:
            host_url = os.environ[base_env_name]
        except KeyError:
            raise AssertionError("fiftyone host must be provided")
    return host_url


def read_51_metadata(metadata_root, task_name, name, grouped, db_url=0):
    metadata_dir = linux_path(metadata_root, "grouped" if grouped else "overlaid")
    task_name_to_dataset_path = linux_path(metadata_dir, "task_name_to_dataset.json.gz")
    # print(f"loading task_name_to_dataset from {task_name_to_dataset_path}")
    task_name_to_dataset: dict = compress_json.load(task_name_to_dataset_path)
    multi_task_name = task_name.replace(name, "multi")
    dataset_name = task_name_to_dataset[multi_task_name]
    db_metadata_dir = linux_path(metadata_dir, dataset_name)
    assert os.path.isdir(db_metadata_dir), f"nonexistent fiftyone metadata_dir: {db_metadata_dir}"
    filename_to_url_path = linux_path(db_metadata_dir, "filename_to_url.json.gz")
    # print(f"loading filename_to_url from {filename_to_url_path}")
    filename_to_51_url: dict = compress_json.load(filename_to_url_path)
    if db_url:
        fo_host_url = get_51_url(grouped=grouped)
        fiftyone_db_url = f"{fo_host_url}/datasets/{dataset_name}"
        return filename_to_51_url, fiftyone_db_url

    return filename_to_51_url


def create_project_lla(cfg_dict, name, label_names, label_cols, client=None):
    if label_names is None:
        label_names = [
            "nucleus",
        ]

    assert len(label_cols) >= len(label_names), "Insufficient number of label_cols"

    if client is None:
        configuration = Configuration(**cfg_dict)
        api_client = ApiClient(configuration)
    else:
        api_client = client

    project_write_request = models.ProjectWriteRequest(
        name=name,
        labels=[
            models.PatchedLabelRequest(
                id=label_id + 1,
                name=label_name,
                color=label_cols[label_id],
                type="any",
                attributes=[
                    {
                        "name": "model",
                        "mutable": True,
                        "input_type": "text",
                        "values": [""],
                        "id": 1,
                        "default_value": "",
                    },
                    {
                        "name": "notes",
                        "mutable": True,
                        "input_type": "text",
                        "values": [""],
                        "id": 2,
                        "default_value": "",
                    },
                ],
            )
            for label_id, label_name in enumerate((label_names))
        ],
    )
    try:
        data, response = api_client.projects_api.create(
            project_write_request,
            # x_organization=x_organization,
            # org=org,
            # org_id=org_id,
        )
        return data
    except exceptions.ApiException as e:
        print("Exception when calling ProjectsApi.create(): %s\n" % e)

    if client is None:
        api_client.close()


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


def create_empty_cvat_task(client, project_id, task_name, task_name_to_id):
    from cvat_sdk.api_client import exceptions

    if task_name in task_name_to_id:
        task_id = task_name_to_id[task_name]
        print(f"deleting existing task: {task_name}")
        try:
            client.api_client.tasks_api.destroy(
                task_id,
            )
        except exceptions.ApiException as e:
            raise AssertionError(f"Failed to delete task:\n{e}")
    try:
        task_spec = {
            "name": task_name,
            "project_id": project_id,
        }
        task, response = client.api_client.tasks_api.create(task_spec)
    except exceptions.ApiException as e:
        raise AssertionError(f"Failed to create task:\n{e}")

    task = client.tasks.retrieve(task.id)

    return task


from cvat_sdk.api_client.api_client import Endpoint


def get_paginated_collection(n_pages, endpoint: Endpoint, *, return_json: bool = False, **kwargs):
    from cvat_sdk.core.helpers import expect_status
    import json

    results = []
    page = 1
    pbar = tqdm(total=n_pages, desc="pages")
    while True:
        page_contents, response = endpoint.call_with_http_info(**kwargs, page=page)
        expect_status(200, response)

        if return_json:
            results.extend(json.loads(response.data).get("results", []))
        else:
            results.extend(page_contents.results)

        pbar.update(1)

        if (
            page_contents is not None
            and not page_contents.next
            or page_contents is None
            and not json.loads(response.data).get("next")
        ):
            break
        page += 1

    return results


def upload_images_hla(client, task, image_paths):
    """
    cvat_sdk/core/proxies/tasks.py
    """

    from cvat_sdk.core.uploading import AnnotationUploader, DataUploader, Uploader

    data = {"image_quality": 70}

    # url = f"/api/tasks/{task.id}/data"
    url = client.api_map.make_endpoint_url(
        client.api_client.tasks_api.create_data_endpoint.path, kwsub={"id": task.id}
    )

    uploader = DataUploader(client)
    response = uploader.upload_files(url, list(map(Path, image_paths)), pbar=None, **data)
    response = json.loads(response.data)
    rq_id = response.get("rq_id")
    assert rq_id, "The rq_id param was not found in the response"

    status_check_period = client.config.status_check_period
    client.logger.info("Awaiting for task %s creation...", task.id)
    client.wait_for_completion(
        rq_id,
        status_check_period=status_check_period,
        log_prefix=f"Task {task.id} creation",
    )
    task.fetch()

    return


def upload_images_lla(client, task, image_paths):
    """
    https://docs.cvat.ai/docs/api_sdk/sdk/reference/apis/tasks-api/#create_data
    https://docs.cvat.ai/docs/api_sdk/sdk/reference/models/data-request/

    """

    from cvat_sdk.api_client.models import DataRequest, StorageMethod, SortingMethod

    upload_finish = True  # bool | Finishes data upload. Can be combined with Upload-Start header to create task data with one request (optional)
    upload_multiple = True  # bool | Indicates that data with this request are single or multiple files that should be attached to a task (optional)
    upload_start = True  # bool | Initializes data upload. Optionally, can include upload metadata in the request body. (optional)
    data_request = DataRequest(
        chunk_size=0,
        image_quality=1,
        start_frame=0,
        stop_frame=0,
        frame_filter="frame_filter_example",
        client_files=[],
        server_files=image_paths,
        remote_files=[],
        use_zip_chunks=False,
        server_files_exclude=[],
        cloud_storage_id=1,
        use_cache=False,
        copy_data=False,
        storage_method=StorageMethod("file_system"),
        sorting_method=SortingMethod("lexicographical"),
        # filename_pattern="filename_pattern_example",
        # job_file_mapping=[
        #     [
        #         "a",
        #     ],
        # ],
        # upload_file_order=[
        #     "upload_file_order_example",
        # ],
        # validation_params=DataRequestValidationParams(None),
    )

    try:
        data, response = client.tasks_api.create_data(
            task.id,
            upload_finish=upload_finish,
            upload_multiple=upload_multiple,
            upload_start=upload_start,
            data_request=data_request,
        )
        pprint(data)
    except exceptions.ApiException as e:
        raise AssertionError("Exception when calling TasksApi.create_data(): %s\n" % e)


def get_cvat_tasks_lla(client, check_duplicates=True):
    print("getting tasks list with low level api...")

    tasks_info = list(client.tasks_api.list())

    n_tasks = tasks_info[0]["count"]
    tasks_per_page = len(tasks_info[0]["results"])
    n_pages = int(math.ceil(n_tasks / tasks_per_page))

    tasks = get_paginated_collection(n_pages, client.tasks_api.list_endpoint)

    if check_duplicates:
        # print("task_names...")
        task_names = [task["name"] for task in tasks]
        # print("unique_task_names...")
        unique_task_names = set()
        duplicate_task_names = [
            task_name
            for task_name in task_names
            if task_name in unique_task_names or unique_task_names.add(task_name)
        ]
        if duplicate_task_names:
            raise AssertionError(f"duplicate tasks found:\n{duplicate_task_names}")

    task_name_to_id = {task["name"]: task["id"] for task in tasks}

    return task_name_to_id


def get_cvat_tasks_hla(client, check_duplicates=True):
    print("getting tasks list with high level api...")
    # tasks = client.tasks
    tasks_dict = [task._model.to_dict() for task in tqdm(client.tasks.list())]
    if check_duplicates:
        # print("task_names...")
        task_names = [task["name"] for task in tasks_dict]
        # print("unique_task_names...")
        unique_task_names = set()
        duplicate_task_names = [
            task_name
            for task_name in task_names
            if task_name in unique_task_names or unique_task_names.add(task_name)
        ]
        if duplicate_task_names:
            raise AssertionError(f"duplicate tasks found:\n{duplicate_task_names}")

    task_name_to_id = {task["name"]: task["id"] for task in tasks_dict}

    return task_name_to_id


def delete_cvat_task_hla(client, task_name):
    task_name_to_id = get_cvat_tasks_hla(client)
    if task_name in task_name_to_id:
        print(f"deleting task: {task_name}")
        task_id = task_name_to_id[task_name]
        task = client.tasks.retrieve(task_id)
        task.remove()
        del task_name_to_id[task_name]
    else:
        print(f"task not found: {task_name}")
    return task_name_to_id


def get_cvat_projects_lla(client):
    # projects = list(client.projects_api.list())
    # projects = projects[0]["results"]

    from cvat_sdk.core.helpers import get_paginated_collection

    projects = get_paginated_collection(client.projects_api.list_endpoint)

    project_name_to_id = {project["name"]: project["id"] for project in projects}
    # project_name_to_dict = {
    #     project["name"]: project for project in projects_dict
    # }
    return project_name_to_id


def get_cvat_projects_hla(client):
    projects = list(client.projects.list())
    projects_dict = [project.__dict__ for project in projects]
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


def to_contour_cv(mask_img_gs):
    contour_pts, _ = cv2.findContours(mask_img_gs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    contour_pts = contour_pts[0]
    contour_pts = contour_pts.squeeze().tolist()
    contour_pts_flat = [x for xs in contour_pts for x in xs]
    return contour_pts_flat


def to_contour(mask):
    # mask.shape
    contours = find_contours(mask)
    contour = contours[0]
    contour = np.flip(contour, axis=1)
    contour = approximate_polygon(contour, tolerance=2.5)
    return contour


def box_iou_batch(boxes_a: np.ndarray, boxes_b: np.ndarray) -> np.ndarray:
    def box_area(box):
        return (box[2] - box[0]) * (box[3] - box[1])

    area_a = box_area(boxes_a.T)
    area_b = box_area(boxes_b.T)

    top_left = np.maximum(boxes_a[:, None, :2], boxes_b[:, :2])
    bottom_right = np.minimum(boxes_a[:, None, 2:], boxes_b[:, 2:])

    area_inter = np.prod(np.clip(bottom_right - top_left, a_min=0, a_max=None), 2)

    return area_inter / (area_a[:, None] + area_b - area_inter)


def perform_nms_fast(objs, enable_mask, iou_threshold):
    assert not enable_mask, "fast nms does not support mask IOU"
    iou_threshold /= 100.0

    obj_conf_arr = np.asarray([obj["confidence"] for obj in objs])
    sort_index = np.flip(obj_conf_arr.argsort())

    boxes = np.asarray([obj["bbox"] for obj in objs])
    categories = np.asarray([obj["class_id"] for obj in objs])

    n_objs = len(objs)

    boxes = boxes[sort_index]
    categories = categories[sort_index]

    ious = box_iou_batch(boxes, boxes)
    ious = ious - np.eye(n_objs)

    keep = np.ones(n_objs, dtype=bool)

    for index, (iou, category) in enumerate(zip(ious, categories, strict=True)):
        if not keep[index]:
            continue

        condition = (iou > iou_threshold) & (categories == category)
        keep = keep & ~condition

    keep = keep[sort_index.argsort()]
    n_del = 0
    for obj, keep_ in enumerate(zip(objs, keep, strict=True)):
        if not keep_:
            obj["to_delete"] = 1
            n_del += 1
    return n_del


def mask_pts_to_img(mask_pts, img_h, img_w):
    mask_img = np.zeros((img_h, img_w), dtype=np.uint8)
    mask_img = cv2.fillPoly(
        mask_img,
        np.array(
            [
                mask_pts,
            ],
            dtype=np.int32,
        ),
        1,
    )

    # mask_img_vis = (mask_img * 255).astype(np.uint8)
    # mask_img_vis = resize_ar(mask_img_vis, 1280, 720)
    # cv2.imshow('mask_img_vis', mask_img_vis)
    # cv2.waitKey(0)

    bin_mask_img = mask_img.astype(bool)

    return bin_mask_img


def overlaps_with_mask(tile_cell, tile_tissue_mask):
    min_x, min_y, max_x, max_y = tile_cell["tile_bbox"]
    cell_mask = tile_cell["mask"].astype(bool)
    tissue_mask = tile_tissue_mask[min_y:max_y, min_x:max_x]
    n_inter = np.count_nonzero(np.logical_and(cell_mask, tissue_mask))
    if n_inter == 0:
        return False
    return True


def get_mask_iou(mask_det, mask_gt, bb_det, bb_gt):
    x1_det, y1_det, x2_det, y2_det = bb_det
    x1_gt, y1_gt, x2_gt, y2_gt = bb_gt

    min_x, min_y = int(min(x1_det, x1_gt)), int(min(y1_det, y1_gt))
    max_x, max_y = int(max(x2_det, x2_gt)), int(max(y2_det, y2_gt))

    mask_det_ = mask_det[min_y : max_y + 1, min_x : max_x + 1]
    mask_gt_ = mask_gt[min_y : max_y + 1, min_x : max_x + 1]

    # mask_det_ = mask_det_ > 0
    # mask_gt_ = mask_gt_ > 0

    mask_union = np.logical_or(mask_det_, mask_gt_)
    n_mask_union = np.count_nonzero(mask_union)

    if n_mask_union == 0:
        return 0

    mask_inter = np.logical_and(mask_det_, mask_gt_)
    n_mask_inter = np.count_nonzero(mask_inter)

    mask_iou = n_mask_inter / n_mask_union

    return mask_iou


def enclose_mask(bbox, mask, roi):
    """
    enclose mask corresponding to bbox inside roi
    """

    w, h = roi[2] - roi[0], roi[3] - roi[1]

    shifted_mask = np.zeros((h, w), dtype=bool)

    shifted_bbox = add_offset(bbox, (-roi[0], -roi[1]))
    min_x, min_y, max_x, max_y = shifted_bbox
    shifted_mask[min_y:max_y, min_x:max_x] = mask

    return shifted_mask, shifted_bbox


def add_offset(bbox, offset):
    return (bbox[0] + offset[0], bbox[1] + offset[1], bbox[2] + offset[0], bbox[3] + offset[1])


def get_cell_ioa(cell1, cell2, vis):
    """
    IOA between two cells from two different but overlapping tiles
    """

    bb_union = get_union(cell1["wsi_bbox"], cell2["wsi_bbox"])

    """move both masks to common frame of reference"""
    mask1, bbox1 = enclose_mask(
        bbox=cell1["wsi_bbox"],
        mask=cell1["mask"],
        roi=bb_union,
    )
    mask2, bbox2 = enclose_mask(
        bbox=cell2["wsi_bbox"],
        mask=cell2["mask"],
        roi=bb_union,
    )

    mask_inter = np.logical_and(mask1, mask2)
    inter_area = np.count_nonzero(mask_inter)

    if inter_area == 0:
        return 0

    min_area = min(cell1["area"], cell2["area"])

    mask_ioa = inter_area / min_area

    if vis:
        print(f"\ninter_area: {inter_area}")
        print(f"min_area: {min_area}")
        print(f"mask_ioa: {mask_ioa}\n")

        h, w = mask1.shape[:2]
        vis_img = np.zeros((h, w, 3), dtype=np.uint8)
        vis_img1 = np.zeros((h, w, 3), dtype=np.uint8)
        vis_img2 = np.zeros((h, w, 3), dtype=np.uint8)

        draw_box(vis_img, bbox1, color=(255, 0, 0))
        vis_img[mask1] = (0, 255, 0)
        draw_box(vis_img1, bbox1, color=(255, 0, 0))
        vis_img1[mask1] = (0, 255, 0)

        draw_box(vis_img, bbox2, color=(0, 0, 255))
        vis_img[mask2] = (0, 255, 0)
        draw_box(vis_img2, bbox2, color=(0, 0, 255))
        vis_img2[mask2] = (0, 255, 0)

        vis_img = resize_ar(vis_img, max=400)
        vis_img1 = resize_ar(vis_img1, max=400)
        vis_img2 = resize_ar(vis_img2, max=400)

        cv2.imshow("enclose_mask", vis_img)
        cv2.imshow("enclose_mask 1", vis_img1)
        cv2.imshow("enclose_mask 2", vis_img2)
        k = cv2.waitKey(0)
        if k == 27:
            exit(0)

    return mask_ioa


def get_mask_ioa(mask_det, mask_gt, bb_det, bb_gt):
    x1_det, y1_det, x2_det, y2_det = bb_det
    x1_gt, y1_gt, x2_gt, y2_gt = bb_gt

    min_x, min_y = int(min(x1_det, x1_gt)), int(min(y1_det, y1_gt))
    max_x, max_y = int(max(x2_det, x2_gt)), int(max(y2_det, y2_gt))

    mask_det_ = mask_det[min_y : max_y + 1, min_x : max_x + 1]
    mask_gt_ = mask_gt[min_y : max_y + 1, min_x : max_x + 1]

    mask_inter = np.logical_and(mask_det_, mask_gt_)
    n_mask_inter = np.count_nonzero(mask_inter)

    if n_mask_inter == 0:
        return 0

    area_det = np.count_nonzero(mask_det)
    area_gt = np.count_nonzero(mask_gt)

    min_area = min(area_det, area_gt)

    mask_ioa = n_mask_inter / min_area

    return mask_ioa


def get_iou(bb_det, bb_gt, xywh=False):
    if xywh:
        det_x1, det_y1, det_w, det_h = bb_det
        gt_x1, gt_y1, gt_w, gt_h = bb_gt
        det_x2, det_y2 = det_x1 + det_w - 1, det_y1 + det_h - 1
        gt_x2, gt_y2 = gt_x1 + gt_w - 1, gt_y1 + gt_h - 1
    else:
        det_x1, det_y1, det_x2, det_y2 = bb_det
        gt_x1, gt_y1, gt_x2, gt_y2 = bb_gt

        det_w, det_h = det_x2 - det_x1 + 1, det_y2 - det_y1 + 1
        gt_w, gt_h = gt_x2 - gt_x1 + 1, gt_y2 - gt_y1 + 1

    bi = [max(det_x1, gt_x1), max(det_y1, gt_y1), min(det_x2, gt_x2), min(det_y2, gt_y2)]

    iw = bi[2] - bi[0] + 1
    ih = bi[3] - bi[1] + 1

    if iw <= 0 or ih <= 0:
        return 0

    ua = (det_w * det_h) + (gt_w * gt_h) - (iw * ih)

    # compute overlap (IoU) = area of intersection / area of union
    ov = iw * ih / ua

    return ov


def get_ioa(bb_det, bb_gt, xywh=False):
    """
    compute overlap (IoA) = area of intersection / area of smaller box
    """

    if xywh:
        det_x1, det_y1, det_w, det_h = bb_det
        gt_x1, gt_y1, gt_w, gt_h = bb_gt
        det_x2, det_y2 = det_x1 + det_w - 1, det_y1 + det_h - 1
        gt_x2, gt_y2 = gt_x1 + gt_w - 1, gt_y1 + gt_h - 1
    else:
        det_x1, det_y1, det_x2, det_y2 = bb_det
        gt_x1, gt_y1, gt_x2, gt_y2 = bb_gt

        det_w, det_h = det_x2 - det_x1 + 1, det_y2 - det_y1 + 1
        gt_w, gt_h = gt_x2 - gt_x1 + 1, gt_y2 - gt_y1 + 1

    bi = [max(det_x1, gt_x1), max(det_y1, gt_y1), min(det_x2, gt_x2), min(det_y2, gt_y2)]

    iw = bi[2] - bi[0] + 1
    ih = bi[3] - bi[1] + 1

    if iw <= 0 or ih <= 0:
        return 0

    area_det = det_w * det_h
    area_gt = gt_w * gt_h

    min_area = min(area_det, area_gt)

    ov = iw * ih / min_area

    return ov


def remove_duplicates(obj_pairs, model_heuristics=True):
    pbar = obj_pairs
    # pbar =  tqdm(pbar, desc="removing duplicates", total=len(obj_pairs))
    for obj_pair in pbar:

        obj1, obj2, ioa = obj_pair

        if obj1["to_delete"] or obj2["to_delete"]:
            continue

        if not model_heuristics:
            if obj1["area"] > obj2["area"]:
                obj2["to_delete"] = 1
            else:
                obj1["to_delete"] = 1
            continue

        model_pair = [obj1["model"], obj2["model"]]
        if "instanseg" in model_pair and "cellpose" in model_pair:
            """cellpose has less tight detections than instanseg (i.e. it can include an area of FP around the nucleus)
            so keep instanseg nucleus when it conflicts with cellpose nucleus"""
            if obj1["model"] == "instanseg":
                obj2["to_delete"] = 1
            else:
                obj1["to_delete"] = 1
        else:
            """
            if the big nucleus overlaps with two or more nuclei from another model, assume that the big one falsely combines multiple smaller nuclei that are correctly detected by the other model
            otherwise assume that the small nucleus is the false detection representing a partial nuclwus from a bad model
            """
            big, small = (obj1, obj2) if obj1["area"] > obj2["area"] else (obj2, obj1)
            overlapping_models = []
            for _, obj in big["overlaps_with"]:
                if obj["to_delete"] or obj["area"] > big["area"]:
                    continue

                if obj["model"] in overlapping_models:
                    big["to_delete"] = 1
                    break

                overlapping_models.append(obj["model"])
            else:
                # for ioa, obj in big["overlaps_with"]:
                # obj["to_delete"] = 1
                small["to_delete"] = 1


def get_job_url(client: Client, task: Task, task_name: str):
    jobs = task.get_jobs()

    assert len(jobs) > 0, f"no jobs found in task: {task_name}"

    if len(jobs) > 1:
        job_ids = [job.id for job in jobs]
        print(f"multiple jobs found in task: {task_name}:\n{job_ids}")
        job_id = min(job_ids)
    else:
        job_id = jobs[0].id

    base_url = client.api_map.host
    task_id = task.id

    job_url = f"{base_url}/tasks/{task_id}/jobs/{job_id}"
    return job_url


def save_annotations_to_cache(annotations, project_name, model_suffix, task_name):
    json_dir = linux_path(".cache", project_name, model_suffix)
    os.makedirs(json_dir, exist_ok=True)
    cache_json_path = linux_path(json_dir, f"{task_name}.json.gz")
    if os.path.exists(cache_json_path):
        print(f"{task_name}:{model_suffix} ::  skipping already existent cache: {cache_json_path}")
        return
    # print(f"{task_name}:{model_suffix} ::  saving annotations to cache: {cache_json_path}")
    compress_json.dump(annotations, cache_json_path, json_kwargs=dict(indent=4))


def load_annotations_from_cache(project_name, model_suffix, task_name):
    json_root_dir = linux_path(".cache", project_name)
    json_dirs = [k for k in os.listdir(json_root_dir) if k.startswith(model_suffix)]
    assert json_dirs, f"no matching json_dirs found for model {model_suffix}"
    assert len(json_dirs) == 1, f"multiple matching json_dirs found for model {model_suffix}"

    cache_json_path = linux_path(json_root_dir, json_dirs[0], f"{task_name}.json.gz")
    # print(f"{task_name}:{model_suffix} ::  loading annotations from cache {cache_json_path}")
    annotations = compress_json.load(cache_json_path)
    return annotations


def get_cvat_annotations(client: Client, task_id):

    task: Task = client.tasks.retrieve(task_id)
    frames_info = task.get_frames_info()
    jobs = task.get_jobs()

    assert len(jobs) == 1, "multiple jobs found in task"

    base_url = client.api_map.host
    task_id = task.id
    job_id = jobs[0].id

    job_url = f"{base_url}/tasks/{task_id}/jobs/{job_id}"

    frame_name_to_info = {frame_info["name"]: frame_info for frame_info in frames_info}
    annotations = task.get_annotations()
    # annotations = client.api_client.tasks_api.retrieve_annotations(task_id, _async_call=False)

    shapes = annotations["shapes"]
    # frames_dicts = [frame_info.to_dict() for frame_info in frames_info]
    frame_name_to_shapes = defaultdict(list)
    pbar = tqdm(shapes, position=0, leave=True)
    for shape in pbar:
        frame_id = shape["frame"]
        frame_name = frames_info[frame_id]["name"]

        shape_dict = shape.to_dict()

        frame_url = f"{job_url}?frame={frame_id}"
        # frame_name_to_info[frame_name]["url"] = frame_url
        shape_dict["frame_url"] = frame_url

        shape_id = shape_dict["id"]
        shape_url = f"{frame_url}&type=shape&serverID={shape_id}"
        shape_dict["url"] = shape_url

        frame_name_to_shapes[frame_name].append(shape_dict)

        # pbar.set_description(
        #     f"{model_str} frame {frame_id} {frame_name} {len(frame_name_to_shapes[frame_name])} objs"
        # )
    return frame_name_to_shapes, frame_name_to_info


def have_overlap(shape_1, shape_2, enable_mask, nms_thresh):
    bbox1, bbox2 = shape_1["bbox"], shape_2["bbox"]
    x1min, y1min, x1max, y1max = bbox1
    x2min, y2min, x2max, y2max = bbox2
    if x1min < x2max and x2min < x1max and y1min < y2max and y2min < y1max:
        if enable_mask:
            """if a small detection is completely covered by a large detection, the small one can escape the filtering process since the the area of union is equal to the area of the large detection while the area of intersection is equal to the area of the small detection so if the latter is small enough, the ratio between them might will be less than nms_thresh"""
            # iou = get_mask_iou(obj1["mask"], obj2["mask"], obj1["bbox"], obj2["bbox"])
            ioa = get_mask_ioa(shape_1["mask"], shape_2["mask"], shape_1["bbox"], shape_2["bbox"])
        else:
            # iou = get_iou(obj1["bbox"], obj2["bbox"], xywh=False)
            ioa = get_ioa(bbox1, bbox2, xywh=False)
        if ioa > nms_thresh:
            shape_1["overlaps_with"].append((ioa, shape_2))
            shape_2["overlaps_with"].append((ioa, shape_1))
            return True

    return False


def apply_offset_to_mask(mask_rgb, max_cell_id, all_rgb_cols, rgb_cols_to_id):
    mask_rgb_flat = mask_rgb.reshape(-1, mask_rgb.shape[2])
    unique_rgb_vals = np.unique(mask_rgb_flat, axis=0)
    unique_rgb_vals = unique_rgb_vals.tolist()
    unique_rgb_vals.remove([0, 0, 0])

    unique_ids = list(rgb_cols_to_id[tuple(rgb_val)] for rgb_val in unique_rgb_vals)

    # assert 0 not in unique_ids, "0 should not be in unique_ids"
    # unique_ids.remove(0)

    offset_ids = [k + max_cell_id for k in unique_ids]

    mask_offset_flat = np.zeros_like(mask_rgb_flat)
    for rgb_val, offset_id in zip(unique_rgb_vals, offset_ids, strict=True):
        # https://stackoverflow.com/a/62642126
        mask_offset_flat[(mask_rgb_flat == rgb_val).all(axis=1)] = all_rgb_cols[offset_id]
    mask_offset = mask_offset_flat.reshape(mask_rgb.shape)

    # Image.fromarray(mask_offset).show("mask_offset")
    # Image.fromarray(mask_rgb).show("mask_rgb")

    # cv2.imshow("mask_rgb", mask_rgb)
    # cv2.imshow("mask_offset", mask_offset)
    # cv2.waitKey(0)

    if offset_ids:
        max_cell_id = max(offset_ids)

    return mask_offset, max_cell_id


def remove_offset_from_mask(mask_rgb, all_rgb_cols):
    mask_rgb_flat = mask_rgb.reshape(-1, mask_rgb.shape[2])
    unique_rgb_vals = np.unique(mask_rgb_flat, axis=0)
    unique_rgb_vals = unique_rgb_vals.tolist()
    unique_rgb_vals.remove([0, 0, 0])
    mask_deoffset_flat = np.zeros_like(mask_rgb_flat)
    for rgb_id, rgb_val in enumerate(unique_rgb_vals):
        # https://stackoverflow.com/a/62642126
        mask_deoffset_flat[(mask_rgb_flat == rgb_val).all(axis=1)] = all_rgb_cols[rgb_id + 1]
    mask_deoffset = mask_deoffset_flat.reshape(mask_rgb.shape)

    return mask_deoffset


def instance_mask_to_ids(mask):
    cell_ids = np.unique(mask)
    invalid_idx = np.argwhere(cell_ids <= 0)
    cell_ids = np.delete(cell_ids, invalid_idx)
    return cell_ids


def class_mask_to_id(cls_mask, inst_mask, bbox):
    xmin, ymin, xmax, ymax = bbox
    cls_mask_cropped = cls_mask[ymin : ymax + 1, xmin : xmax + 1]

    cls_mask_cropped2 = np.copy(cls_mask_cropped)
    cls_mask_cropped2[np.logical_not(inst_mask)] = 0
    class_ids = instance_mask_to_ids(cls_mask_cropped2)

    assert len(class_ids) > 0, "no class_ids found for cell"
    assert len(class_ids) == 1, "multiple class_ids found for cell"

    class_id = int(class_ids[0])
    assert class_id > 0, "class_id must be > 0"
    return class_id


def instance_mask_to_rgb(mask, cols):

    cell_ids = instance_mask_to_ids(mask)

    h, w = mask.shape
    rgb_mask = np.zeros((h, w, 3), dtype=np.uint8)
    n_cols = len(cols)

    for col_id, cell_id in enumerate(cell_ids):
        rgb_mask[mask == cell_id] = hex_to_rgb(cols[col_id % n_cols])

    return rgb_mask


def overlay_cells(img, mask_rgb, alpha):
    mask_rgb_flat = mask_rgb.reshape(-1, mask_rgb.shape[2])

    unique_rgb_vals, unique_inverse = np.unique(mask_rgb_flat, axis=0, return_inverse=True)
    unique_rgb_vals = unique_rgb_vals.tolist()
    unique_rgb_vals.remove([0, 0, 0])

    img_flat = img.reshape(-1, img.shape[2]).copy()
    # img_flat = img_flat.astype(np.float32)
    # mask_rgb_flat = mask_rgb_flat.astype(np.float32)

    cell_mask = unique_inverse > 0
    img_flat[cell_mask] = img_flat[cell_mask] * (1 - alpha) + mask_rgb_flat[cell_mask] * alpha

    # for rgb_val in unique_rgb_vals:
    #     # https://stackoverflow.com/a/62642126
    #     cell_mask = (mask_rgb_flat == rgb_val).all(axis=1)
    #     # rgb_val_np = np.asarray(rgb_val, dtype=np.float32)
    #     img_flat[cell_mask] = img_flat[cell_mask] * (1 - alpha) + mask_rgb_flat[cell_mask] * alpha

    img_vis = img_flat.reshape(img.shape).astype(np.uint8)
    return img_vis


def blend_mask(mask, image, alpha=0.5):
    vis_image = np.copy(image)
    vis_image = vis_image * (1 - alpha) + mask * alpha


def draw_box(
    frame,
    box,
    _id=None,
    color=(255, 255, 255),
    thickness=1,
    transparency=0.0,
    xywh=True,
    norm=False,
    mask=None,
    alpha=0.5,
):
    """
    :type frame: np.ndarray
    :type _id: int | str | None
    :param color: indexes into col_bgr
    :type color: str
    :type thickness: int
    :type is_dotted: int
    :type transparency: float
    :rtype: None
    """
    if not isinstance(box, np.ndarray):
        box = np.asarray(box)

    if np.any(np.isnan(box)):
        print("invalid location provided: {}".format(box))
        return

    if isinstance(box, np.ndarray):
        box = list(box.squeeze())

    if xywh:
        x1, y1, w, h = box
        x2, y2 = x1 + w, y1 + h
    else:
        x1, y1, x2, y2 = box

    pt1, pt2 = (x1, y1), (x2, y2)
    img_h, img_w = frame.shape[:2]

    if norm:
        pt1 = (pt1[0] * img_w, pt1[1] * img_h)
        pt2 = (pt2[0] * img_w, pt2[1] * img_h)

    pt1 = tuple(map(int, pt1))
    pt2 = tuple(map(int, pt2))

    if transparency > 0:
        _frame = np.copy(frame)
    else:
        _frame = frame

    if mask is None:
        cv2.rectangle(_frame, pt1, pt2, color, thickness=thickness)

    if transparency > 0:
        frame[pt1[1] : pt2[1], pt1[0] : pt2[0], ...] = (
            frame[pt1[1] : pt2[1], pt1[0] : pt2[0], ...].astype(np.float32) * (1 - transparency)
            + _frame[pt1[1] : pt2[1], pt1[0] : pt2[0], ...].astype(np.float32) * transparency
        ).astype(frame.dtype)

    if _id is not None:
        font_line_type = cv2.LINE_AA
        cv2.putText(
            frame,
            str(_id),
            (int(box[0] - 1), int(box[1] - 1)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            font_line_type,
        )
    if mask is not None:
        if isinstance(color, str):
            color = hex_to_rgb(color)

        color = np.asarray(color, dtype=np.float32)
        full_mask = np.zeros((img_h, img_w), dtype=bool)
        full_mask[y1:y2, x1:x2] = mask
        frame[full_mask] = frame[full_mask].astype(np.float32) * (1 - alpha) + color * alpha


def add_suffix(src_path, suffix, dst_ext="", sep="_", src_ext=""):
    # abs_src_path = os.path.abspath(src_path)
    src_dir, src_name = os.path.dirname(src_path), os.path.basename(src_path)

    if not src_ext:
        src_name, src_ext = os.path.splitext(src_name)
    else:
        src_name = src_name.replace(src_ext, "")

    if not dst_ext:
        dst_ext = src_ext

    dst_path = linux_path(src_dir, src_name + sep + suffix + dst_ext)
    return dst_path


def linux_path(*args, **kwargs):
    return os.path.join(*args, **kwargs).replace(os.sep, "/")


def hex_to_rgb(hex):
    if isinstance(hex, str):
        return tuple(int(hex[i : i + 2], 16) for i in (1, 3, 5))
    return hex


def mask_rgb_to_id(mask_rgb, rgb_cols_to_id):
    unique_rgb_vals = np.unique(mask_rgb.reshape(-1, mask_rgb.shape[2]), axis=0)
    unique_ids = list(rgb_cols_to_id[tuple(rgb_val)] for rgb_val in unique_rgb_vals)

    mask_h, mask_w = mask_rgb.shape[:2]
    mask_id = np.zeros((mask_h, mask_w), dtype=np.int32)
    for rgb_val, unique_id in zip(unique_rgb_vals, unique_ids, strict=True):
        if unique_id == 0:
            continue
        mask_id[mask_rgb == rgb_val] = unique_id

    return mask_id


def sleep_with_pbar(sleep_t, desc=""):
    pbar = tqdm(range(sleep_t))
    if desc:
        pbar.set_description(desc)
    for _ in pbar:
        time.sleep(1)


def to_str_multi(relevant_task_names, item_sep="\t", line_sep="\n"):
    return line_sep.join(item_sep.join(k) for k in zip(*relevant_task_names, strict=True))


def to_str(relevant_task_names, sep="\n"):
    return sep.join(relevant_task_names)


class CVConstants:
    similarity_types = {
        0: cv2.TM_CCOEFF_NORMED,
        1: cv2.TM_SQDIFF_NORMED,
        2: cv2.TM_CCORR_NORMED,
        3: cv2.TM_CCOEFF,
        4: cv2.TM_SQDIFF,
        5: cv2.TM_CCORR,
    }
    interp_types = {
        0: cv2.INTER_NEAREST,
        1: cv2.INTER_LINEAR,
        2: cv2.INTER_AREA,
        3: cv2.INTER_CUBIC,
        4: cv2.INTER_LANCZOS4,
    }
    fonts = {
        0: cv2.FONT_HERSHEY_SIMPLEX,
        1: cv2.FONT_HERSHEY_PLAIN,
        2: cv2.FONT_HERSHEY_DUPLEX,
        3: cv2.FONT_HERSHEY_COMPLEX,
        4: cv2.FONT_HERSHEY_TRIPLEX,
        5: cv2.FONT_HERSHEY_COMPLEX_SMALL,
        6: cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
        7: cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
    }
    line_types = {
        0: cv2.LINE_4,
        1: cv2.LINE_8,
        2: cv2.LINE_AA,
    }


class CVText:
    def __init__(
        self,
        color="white",
        bkg_color="black",
        location=0,
        font=5,
        size=0.8,
        thickness=1,
        line_type=2,
        offset=(5, 25),
    ):
        self.color = color
        self.bkg_color = bkg_color
        self.location = location
        self.font = font
        self.size = size
        self.thickness = thickness
        self.line_type = line_type
        self.offset = offset

        self.help = {
            "font": "Available fonts: "
            "0: cv2.FONT_HERSHEY_SIMPLEX, "
            "1: cv2.FONT_HERSHEY_PLAIN, "
            "2: cv2.FONT_HERSHEY_DUPLEX, "
            "3: cv2.FONT_HERSHEY_COMPLEX, "
            "4: cv2.FONT_HERSHEY_TRIPLEX, "
            "5: cv2.FONT_HERSHEY_COMPLEX_SMALL, "
            "6: cv2.FONT_HERSHEY_SCRIPT_SIMPLEX ,"
            "7: cv2.FONT_HERSHEY_SCRIPT_COMPLEX; ",
            "location": "0: top left, 1: top right, 2: bottom right, 3: bottom left; ",
            "bkg_color": "should be empty for no background",
        }


def stack_images_with_resize(
    img_list,
    grid_size=None,
    stack_order=0,
    borderless=1,
    preserve_order=0,
    return_idx=0,
    # annotations=None,
    # ann_fmt=(0, 5, 15, 1, 1, 255, 255, 255, 0, 0, 0),
    only_height=0,
    only_border=1,
):
    n_images = len(img_list)
    # print('grid_size: {}'.format(grid_size))

    if grid_size is None:
        n_cols = n_rows = int(np.ceil(np.sqrt(n_images)))
    else:
        n_rows, n_cols = grid_size

        if n_rows < 0:
            n_rows = int(np.ceil(n_images / n_cols))
        elif n_cols < 0:
            n_cols = int(np.ceil(n_images / n_rows))

    target_ar = 1920.0 / 1080.0
    if n_cols <= n_rows:
        target_ar /= 2.0
    shape_img_id = 0
    min_ar_diff = np.inf
    img_heights = np.zeros((n_images,), dtype=np.int32)
    for _img_id in range(n_images):
        height, width = img_list[_img_id].shape[:2]
        img_heights[_img_id] = height
        img_ar = float(n_cols * width) / float(n_rows * height)
        ar_diff = abs(img_ar - target_ar)
        if ar_diff < min_ar_diff:
            min_ar_diff = ar_diff
            shape_img_id = _img_id

    img_heights_sort_idx = np.argsort(-img_heights)
    row_start_idx = img_heights_sort_idx[:n_rows]
    img_idx = img_heights_sort_idx[n_rows:]
    # print('img_heights: {}'.format(img_heights))
    # print('img_heights_sort_idx: {}'.format(img_heights_sort_idx))
    # print('img_idx: {}'.format(img_idx))

    # grid_size = [n_rows, n_cols]
    img_size = img_list[shape_img_id].shape
    height, width = img_size[:2]

    if only_height:
        width = 0
    # grid_size = [n_rows, n_cols]
    # print 'img_size: ', img_size
    # print 'n_images: ', n_images
    # print 'grid_size: ', grid_size

    # print()
    stacked_img = None
    list_ended = False
    img_idx_id = 0
    inner_axis = 1 - stack_order
    stack_idx = []
    stack_locations = []
    start_row = 0
    # curr_ann = ''
    for row_id in range(n_rows):
        start_id = n_cols * row_id
        curr_row = None
        start_col = 0
        for col_id in range(n_cols):
            img_id = start_id + col_id
            if img_id >= n_images:
                curr_img = np.zeros(img_size, dtype=np.uint8)
                list_ended = True
            else:
                if preserve_order:
                    _curr_img_id = img_id
                elif col_id == 0:
                    _curr_img_id = row_start_idx[row_id]
                else:
                    _curr_img_id = img_idx[img_idx_id]
                    img_idx_id += 1

                curr_img = img_list[_curr_img_id]
                # if annotations:
                #     curr_ann = annotations[_curr_img_id]
                stack_idx.append(_curr_img_id)
                # print(curr_img.shape[:2])

                # if curr_ann:
                #     putTextWithBackground(curr_img, curr_ann, fmt=ann_fmt)

                if not borderless:
                    curr_img = resize_ar(curr_img, width, height, only_border=only_border)
                if img_id == n_images - 1:
                    list_ended = True
            if curr_row is None:
                curr_row = curr_img
            else:
                if borderless:
                    if curr_row.shape[0] < curr_img.shape[0]:
                        curr_row = resize_ar(
                            curr_row, 0, curr_img.shape[0], only_border=only_border
                        )
                    elif curr_img.shape[0] < curr_row.shape[0]:
                        curr_img = resize_ar(
                            curr_img, 0, curr_row.shape[0], only_border=only_border
                        )
                # print('curr_row.shape: ', curr_row.shape)
                # print('curr_img.shape: ', curr_img.shape)
                curr_row = np.concatenate((curr_row, curr_img), axis=inner_axis)

            curr_h, curr_w = curr_img.shape[:2]
            stack_locations.append((start_row, start_col, start_row + curr_h, start_col + curr_w))
            start_col += curr_w

        if stacked_img is None:
            stacked_img = curr_row
        else:
            if borderless:
                resize_factor = float(curr_row.shape[1]) / float(stacked_img.shape[1])
                if curr_row.shape[1] < stacked_img.shape[1]:
                    curr_row = resize_ar(curr_row, stacked_img.shape[1], 0, only_border=only_border)
                elif curr_row.shape[1] > stacked_img.shape[1]:
                    stacked_img = resize_ar(
                        stacked_img, curr_row.shape[1], 0, only_border=only_border
                    )

                new_start_col = 0
                for _i in range(n_cols):
                    _start_row, _start_col, _end_row, _end_col = stack_locations[_i - n_cols]
                    _w, _h = _end_col - _start_col, _end_row - _start_row
                    w_resized, h_resized = _w / resize_factor, _h / resize_factor
                    stack_locations[_i - n_cols] = (
                        _start_row,
                        new_start_col,
                        _start_row + h_resized,
                        new_start_col + w_resized,
                    )
                    new_start_col += w_resized
            # print('curr_row.shape: ', curr_row.shape)
            # print('stacked_img.shape: ', stacked_img.shape)
            stacked_img = np.concatenate((stacked_img, curr_row), axis=stack_order)

        curr_h, curr_w = curr_row.shape[:2]
        start_row += curr_h

        if list_ended:
            break
    if return_idx:
        return stacked_img, stack_idx, stack_locations
    else:
        return stacked_img


def annotate(
    img_list,
    text=None,
    fmt=CVText(),
    no_resize=1,
    grid_size=(-1, 1),
    max_width=0,
    max_height=0,
):
    """

    :param str title:
    :param np.ndarray | list | tuple img_list:
    :param str | logging.RootLogger | CustomLogger text:
    :param int pause:
    :param CVText fmt:
    :param int no_resize:
    :param int n_modules:
    :param int use_plt:
    :param tuple(int) grid_size:
    :return:
    """
    if not isinstance(img_list, (list, tuple)):
        img_list = [
            img_list,
        ]

    size = fmt.size

    # print('self.size: {}'.format(self.size))

    color = [255, 255, 255]
    font = CVConstants.fonts[fmt.font]
    line_type = CVConstants.line_types[fmt.line_type]

    location = list(fmt.offset)

    if "\n" in text:
        text_list = text.split("\n")
    else:
        text_list = [
            text,
        ]

    max_text_width = 0
    text_height = 0
    text_heights = []

    for _text in text_list:
        _text_width, _text_height = cv2.getTextSize(
            _text, font, fontScale=fmt.size, thickness=fmt.thickness
        )[0]
        if _text_width > max_text_width:
            max_text_width = _text_width
        text_height += _text_height + 5
        text_heights.append(_text_height)

    text_width = max_text_width + 10
    text_height += 30

    text_img = np.zeros((text_height, text_width), dtype=np.uint8)
    for _id, _text in enumerate(text_list):
        cv2.putText(text_img, _text, tuple(location), font, size, color, fmt.thickness, line_type)
        location[1] += text_heights[_id] + 5

    text_img = text_img.astype(np.float32) / 255.0

    text_img = np.stack(
        [
            text_img,
        ]
        * 3,
        axis=2,
    )

    for _id, _img in enumerate(img_list):
        if len(_img.shape) == 2:
            _img = np.stack(
                [
                    _img,
                ]
                * 3,
                axis=2,
            )
        if _img.dtype == np.uint8:
            _img = _img.astype(np.float32) / 255.0
        img_list[_id] = _img

    img_stacked = stack_images_with_resize(
        img_list, grid_size=grid_size, preserve_order=1, only_border=no_resize
    )
    img_list_txt = [text_img, img_stacked]

    img_stacked_txt = stack_images_with_resize(
        img_list_txt, grid_size=(2, 1), preserve_order=1, only_border=no_resize
    )
    # img_stacked_txt_res = cv2.resize(img_stacked_txt, (300, 300), fx=0, fy=0)
    # img_stacked_txt_res_gs = cv2.cvtColor(img_stacked_txt_res, cv2.COLOR_BGR2GRAY)

    img_stacked_txt = (img_stacked_txt * 255).astype(np.uint8)

    if img_stacked_txt.shape[0] > max_height > 0:
        img_stacked_txt = resize_ar(img_stacked_txt, height=max_height)

    if img_stacked_txt.shape[1] > max_width > 0:
        img_stacked_txt = resize_ar(img_stacked_txt, width=max_width)

    return img_stacked_txt


def resize_ar(
    src_img,
    width=0,
    height=0,
    max=0,
    return_factors=False,
    placement_type=1,
    only_border=0,
    only_shrink=0,
    strict=False,
    white_bkg=0,
):
    src_height, src_width = src_img.shape[:2]
    src_aspect_ratio = float(src_width) / float(src_height)

    if max > 0:
        if src_height > src_width:
            height = max
        else:
            width = max

    if len(src_img.shape) == 3:
        n_channels = src_img.shape[2]
    else:
        n_channels = 1

    if width <= 0 and height <= 0:
        raise AssertionError("Both width and height cannot be zero")
    elif height <= 0:
        if only_shrink and width > src_width:
            width = src_width
        if only_border:
            height = src_height
        else:
            height = int(width / src_aspect_ratio)
    elif width <= 0:
        if only_shrink and height > src_height:
            height = src_height
        if only_border:
            width = src_width
        else:
            width = int(height * src_aspect_ratio)

    aspect_ratio = float(width) / float(height)

    if strict:
        assert aspect_ratio == src_aspect_ratio, "aspect_ratio mismatch"

    if only_border:
        dst_width = width
        dst_height = height
        if placement_type == 0:
            start_row = start_col = 0
        elif placement_type == 1:
            start_row = int((dst_height - src_height) / 2.0)
            start_col = int((dst_width - src_width) / 2.0)
        elif placement_type == 2:
            start_row = int(dst_height - src_height)
            start_col = int(dst_width - src_width)
        else:
            raise AssertionError("Invalid placement_type: {}".format(placement_type))
    else:

        if src_aspect_ratio == aspect_ratio:
            dst_width = src_width
            dst_height = src_height
            start_row = start_col = 0
        elif src_aspect_ratio > aspect_ratio:
            dst_width = src_width
            dst_height = int(src_width / aspect_ratio)
            start_row = int((dst_height - src_height) / 2.0)
            if placement_type == 0:
                start_row = 0
            elif placement_type == 1:
                start_row = int((dst_height - src_height) / 2.0)
            elif placement_type == 2:
                start_row = int(dst_height - src_height)
            else:
                raise AssertionError("Invalid placement_type: {}".format(placement_type))
            start_col = 0
        else:
            dst_height = src_height
            dst_width = int(src_height * aspect_ratio)
            start_col = int((dst_width - src_width) / 2.0)
            if placement_type == 0:
                start_col = 0
            elif placement_type == 1:
                start_col = int((dst_width - src_width) / 2.0)
            elif placement_type == 2:
                start_col = int(dst_width - src_width)
            else:
                raise AssertionError("Invalid placement_type: {}".format(placement_type))
            start_row = 0

    if white_bkg:
        dst_img = np.full(
            (dst_height, dst_width, n_channels),
            255 if src_img.dtype == np.uint8 else 1.0,
            dtype=src_img.dtype,
        )
    else:
        dst_img = np.zeros((dst_height, dst_width, n_channels), dtype=src_img.dtype)
    dst_img = dst_img.squeeze()

    dst_img[start_row : start_row + src_height, start_col : start_col + src_width, ...] = src_img
    if not only_border:
        dst_img = cv2.resize(dst_img, (width, height))

    if return_factors:
        resize_factor = float(height) / float(dst_height)
        return dst_img, resize_factor, start_row, start_col
    else:
        return dst_img


def _taper_mask(ly=224, lx=224, sig=7.5):
    """
    Generate a taper mask.

    Args:
        ly (int): The height of the mask. Default is 224.
        lx (int): The width of the mask. Default is 224.
        sig (float): The sigma value for the tapering function. Default is 7.5.

    Returns:
        numpy.ndarray: The taper mask.

    """
    bsize = max(224, max(ly, lx))
    xm = np.arange(bsize)
    xm = np.abs(xm - xm.mean())
    mask = 1 / (1 + np.exp((xm - (bsize / 2 - 20)) / sig))
    mask = mask * mask[:, np.newaxis]
    mask = mask[
        bsize // 2 - ly // 2 : bsize // 2 + ly // 2 + ly % 2,
        bsize // 2 - lx // 2 : bsize // 2 + lx // 2 + lx % 2,
    ]
    return mask


def average_tiles(y, ysub, xsub, Ly, Lx):
    """
    Average the results of the network over tiles.

    Args:
        y (float): Output of cellpose network for each tile. Shape: [ntiles x nclasses x bsize x bsize]
        ysub (list): List of arrays with start and end of tiles in Y of length ntiles
        xsub (list): List of arrays with start and end of tiles in X of length ntiles
        Ly (int): Size of pre-tiled image in Y (may be larger than original image if image size is less than bsize)
        Lx (int): Size of pre-tiled image in X (may be larger than original image if image size is less than bsize)

    Returns:
        yf (float32): Network output averaged over tiles. Shape: [nclasses x Ly x Lx]
    """
    Navg = np.zeros((Ly, Lx))
    yf = np.zeros((y.shape[1], Ly, Lx), np.float32)
    # taper edges of tiles
    mask = _taper_mask(ly=y.shape[-2], lx=y.shape[-1])
    for j in range(len(ysub)):
        yf[:, ysub[j][0] : ysub[j][1], xsub[j][0] : xsub[j][1]] += y[j] * mask
        Navg[ysub[j][0] : ysub[j][1], xsub[j][0] : xsub[j][1]] += mask
    yf /= Navg
    return yf


def get_union(bb1, bb2):
    return [
        min(bb1[0], bb2[0]),
        min(bb1[1], bb2[1]),
        max(bb1[2], bb2[2]),
        max(bb1[3], bb2[3]),
    ]


def get_intersection(roi1, roi2):
    return [
        max(roi1[0], roi2[0]),
        max(roi1[1], roi2[1]),
        min(roi1[2], roi2[2]),
        min(roi1[3], roi2[3]),
    ]


def make_tiles(wsi_size, tile_size, tile_overlap, max_tiles, vis):

    wsi_h, wsi_w = wsi_size

    if isinstance(tile_size, int):
        tile_size_y = tile_size_x = tile_size
    else:
        tile_size_y, tile_size_x = tile_size

    if isinstance(tile_overlap, int):
        tile_overlap_y = tile_overlap_x = tile_overlap
    else:
        tile_overlap_y, tile_overlap_x = tile_overlap

    assert tile_size_x > tile_overlap_x, "tile_size_x must be > tile_overlap_x"
    assert tile_size_y > tile_overlap_y, "tile_size_y must be > tile_overlap_y"

    tile_size_y, tile_size_x = min(tile_size_y, wsi_h), min(tile_size_x, wsi_w)

    tile_stride_x, tile_stride_y = tile_size_x - tile_overlap_x, tile_size_y - tile_overlap_y

    y_ends = list(np.arange(tile_size_y, wsi_h + 1, tile_stride_y))
    x_ends = list(np.arange(tile_size_x, wsi_w + 1, tile_stride_x))

    if y_ends[-1] != wsi_h:
        y_ends.append(wsi_h)
    if x_ends[-1] != wsi_w:
        x_ends.append(wsi_w)

    y_starts = [y_end - tile_size_y for y_end in y_ends]
    x_starts = [x_end - tile_size_x for x_end in x_ends]

    # adjust last tile to prevent overflow to outside WSI boundaries
    # if y_ends[-1] > Ly:
    #     offset_y = y_ends[-1] - Ly
    #     y_starts[-1] -= offset_y
    #     y_ends[-1] -= offset_y

    # if x_ends[-1] > Lx:
    #     offset_x = x_ends[-1] - Lx

    #     x_starts[-1] -= offset_x
    #     x_ends[-1] -= offset_x

    grid_size_y, grid_size_x = len(y_starts), len(x_starts)

    tile_id = 0

    grid_to_roi = {}
    tile_id_to_roi = {}

    grid_to_tile_id = {}
    tile_id_to_grid = {}

    overlapping_tiles = []

    for j, i in itertools.product(range(grid_size_y), range(grid_size_x)):

        x1, y1, x2, y2 = (
            x_starts[i],
            y_starts[j],
            x_ends[i],
            y_ends[j],
        )

        assert x2 <= wsi_w and y2 <= wsi_h, f"overflowing tile: {[x1, y1, x2, y2]}"

        tile_roi = [int(x1), int(y1), int(x2), int(y2)]

        # print(f"{(j, i)}: {tile_roi}")

        grid_to_roi[(j, i)] = tile_roi
        tile_id_to_roi[tile_id] = tile_roi

        grid_to_tile_id[(j, i)] = tile_id
        tile_id_to_grid[tile_id] = (j, i)

        if j > 0:
            ovl_tile_id = grid_to_tile_id[(j - 1, i)]
            ovl_tile_roi = tile_id_to_roi[ovl_tile_id]
            overlapping_tiles.append((tile_id, ovl_tile_id))
            inter_roi = get_intersection(tile_roi, ovl_tile_roi)
            ovl_x, ovl_y = inter_roi[2] - inter_roi[0], inter_roi[3] - inter_roi[1]

            if j == grid_size_y - 1:
                assert ovl_y >= tile_overlap_y, "row tile_overlap mismatch"
            else:
                assert ovl_y == tile_overlap_y, "row tile_overlap mismatch"

        if i > 0:
            ovl_tile_id = grid_to_tile_id[(j, i - 1)]
            ovl_tile_roi = tile_id_to_roi[ovl_tile_id]
            overlapping_tiles.append((tile_id, ovl_tile_id))
            inter_roi = get_intersection(tile_roi, ovl_tile_roi)
            ovl_x, ovl_y = inter_roi[2] - inter_roi[0], inter_roi[3] - inter_roi[1]

            if i == grid_size_x - 1:
                assert ovl_x >= tile_overlap_x, "column tile_overlap mismatch"
            else:
                assert ovl_x == tile_overlap_x, "column tile_overlap mismatch"

        if i > 0 and j > 0:
            ovl_tile_id = grid_to_tile_id[(j - 1, i - 1)]
            ovl_tile_roi = tile_id_to_roi[ovl_tile_id]
            overlapping_tiles.append((tile_id, grid_to_tile_id[(j - 1, i - 1)]))
            inter_roi = get_intersection(tile_roi, ovl_tile_roi)
            ovl_x, ovl_y = inter_roi[2] - inter_roi[0], inter_roi[3] - inter_roi[1]

            if i == grid_size_x - 1:
                assert ovl_x >= tile_overlap_x, "column tile_overlap mismatch"
            else:
                assert ovl_x == tile_overlap_x, "column tile_overlap mismatch"

            if j == grid_size_y - 1:
                assert ovl_y >= tile_overlap_y, "row tile_overlap mismatch"
            else:
                assert ovl_y == tile_overlap_y, "row tile_overlap mismatch"

        tile_id += 1

        if tile_id >= max_tiles > 0:
            break

    if vis:
        show_overlapping_tiles((wsi_h, wsi_w), tile_id_to_roi, overlapping_tiles)

    return tile_id_to_roi, overlapping_tiles


def is_overlapping(roi, bbox):
    """
    Check if bbox overlaps with the roi
    """
    return roi[0] < bbox[2] and bbox[0] < roi[2] and roi[1] < bbox[3] and bbox[1] < roi[3]


def is_inside(roi, bbox):
    """
    Check if bbox is entirely contained inside roi
    """
    return roi[0] <= bbox[0] and roi[1] <= bbox[1] and roi[2] >= bbox[2] and roi[3] >= bbox[3]


def remove_duplicates_from_tiles(
    wsi, tile_id_to_roi, tile_id_to_cells, overlapping_tiles, nms_thresh, vis
):
    for id1, id2 in tqdm(
        overlapping_tiles, desc="processing intersecting tiles", total=len(overlapping_tiles)
    ):

        tile1_roi, tile2_roi = tile_id_to_roi[id1], tile_id_to_roi[id2]
        inter_roi = get_intersection(tile1_roi, tile2_roi)

        # tile1_offset1 = (tile1_bbox[0], tile1_bbox[1])
        # tile2_offset1 = (tile2_bbox[0], tile2_bbox[1])

        tile1_cells, tile2_cells = tile_id_to_cells[id1], tile_id_to_cells[id2]

        inter_cells1 = [
            tile_cell
            for tile_cell in tile1_cells
            if is_overlapping(inter_roi, tile_cell["wsi_bbox"])
        ]
        inter_cells2 = [
            tile_cell
            for tile_cell in tile2_cells
            if is_overlapping(inter_roi, tile_cell["wsi_bbox"])
        ]

        cell_pairs = [
            (cell1, cell2, cell1["ioa"][cell2["id"]])
            for cell1, cell2 in itertools.product(inter_cells1, inter_cells2)
            if are_overlapping_cells(cell1, cell2, nms_thresh, vis)
        ]
        """deal with higher overlap pairs first to avoid having to deal with spurious pairs later on"""
        cell_pairs.sort(key=lambda x: x[2], reverse=True)
        # cell_pairs = list(filter(lambda x: x[2] > nms_thresh, cell_pairs))

        remove_duplicates(cell_pairs, model_heuristics=False)

        if vis:
            show_cells(wsi, inter_cells1, tile1_roi, col="#00ff00", title="tile1", pause=0)
            show_cells(wsi, inter_cells2, tile2_roi, col="#ff0000", title="tile2", pause=0)
            show_overlapping_cells(wsi, cell_pairs, inter_roi, cols=("#00ff00", "#ff0000"), pause=0)
            unique_cells = [cell for cell in inter_cells1 + inter_cells2 if not cell["to_delete"]]
            show_cells(wsi, unique_cells, inter_roi, col="#00ff00", title="unique", pause=1)


def show_cells(wsi, cells, roi, col, title, pause):
    tile_img_pil = wsi.read_region(
        location=(roi[0], roi[1]),
        level=0,
        size=(roi[2] - roi[0], roi[3] - roi[1]),
    )
    tile_img = np.array(tile_img_pil)[..., :3]

    for cell in cells:
        bb = add_offset(cell["wsi_bbox"], (-roi[0], -roi[1]))
        # bb = cell["tile_bbox"]

        draw_box(
            tile_img,
            box=bb,
            mask=cell["mask"],
            xywh=False,
            alpha=0.5,
            color=col,
        )
    tile_img_vis = resize_ar(tile_img, max=1200)
    cv2.imshow(title, tile_img_vis)
    k = cv2.waitKey(1 - pause)
    if k == 27:
        exit(0)


def show_overlapping_cells(wsi, cell_pairs, roi, cols, pause):
    roi_img_pil = wsi.read_region(
        location=(roi[0], roi[1]),
        level=0,
        size=(roi[2] - roi[0], roi[3] - roi[1]),
    )
    roi_img = np.array(roi_img_pil)[..., :3]

    for cell_pair in cell_pairs:
        cell1, cell2 = cell_pair[:2]
        col1, col2 = cols
        bb1 = add_offset(cell1["wsi_bbox"], (-roi[0], -roi[1]))
        bb2 = add_offset(cell2["wsi_bbox"], (-roi[0], -roi[1]))

        draw_box(
            roi_img,
            box=bb1,
            mask=cell1["mask"],
            xywh=False,
            alpha=0.5,
            color=col1,
        )
        draw_box(
            roi_img,
            box=bb2,
            mask=cell2["mask"],
            xywh=False,
            alpha=0.5,
            color=col2,
        )
    roi_img_vis = resize_ar(roi_img, max=1200)
    cv2.imshow("roi_img_vis", roi_img_vis)
    k = cv2.waitKey(1 - pause)
    if k == 27:
        exit(0)


def are_overlapping_cells(cell1, cell2, nms_thresh, vis):
    bb1, bb2 = cell1["wsi_bbox"], cell2["wsi_bbox"]
    if bb1[0] < bb2[2] and bb2[0] < bb1[2] and bb1[1] < bb2[3] and bb2[1] < bb1[3]:
        ioa = get_cell_ioa(cell1, cell2, vis)
        if ioa > nms_thresh:
            cell1["ioa"][cell2["id"]] = cell2["ioa"][cell1["id"]] = ioa
            return True
    return False


def show_overlapping_tiles(wsi_size, tile_id_to_roi, overlapping_tiles, vis_factor=32):

    Ly, Lx = wsi_size
    vis_x, vis_y = Lx // vis_factor, Ly // vis_factor
    vis_img = np.zeros((vis_y, vis_x, 3), dtype=np.uint8)

    for tile_id, tile_roi in tile_id_to_roi.items():
        tile_x1, tile_y1, tile_x2, tile_y2 = tile_roi

        vis_tile_x1, vis_tile_x2 = tile_x1 // vis_factor, tile_x2 // vis_factor
        vis_tile_y1, vis_tile_y2 = tile_y1 // vis_factor, tile_y2 // vis_factor

        draw_box(
            vis_img,
            [vis_tile_x1, vis_tile_y1, vis_tile_x2, vis_tile_y2],
            color=(255, 255, 255),
            xywh=False,
        )

        # vis_img_res = resize_ar(vis_img, max=600)
        # cv2.imshow("vis_img_res", vis_img_res)
        # k = cv2.waitKey(0)
        # if k == 27:
        #     exit(0)

    print(f"found {len(overlapping_tiles)} overlapping_tiles")

    for id1, id2 in overlapping_tiles:
        tile1_vis = [k // vis_factor for k in tile_id_to_roi[id1]]
        tile2_vis = [k // vis_factor for k in tile_id_to_roi[id2]]
        inter_vis = get_intersection(tile1_vis, tile2_vis)

        vis_img_ov = np.copy(vis_img)

        draw_box(vis_img_ov, tile1_vis, color=(0, 255, 0), xywh=False)
        draw_box(vis_img_ov, tile2_vis, color=(0, 0, 255), xywh=False)
        draw_box(vis_img_ov, inter_vis, color=(255, 0, 0), xywh=False)

        vis_img_ov = resize_ar(vis_img_ov, max=600)

        print(vis_img_ov.shape)

        cv2.imshow("vis_img_ov", vis_img_ov)
        k = cv2.waitKey(0)
        if k == 27:
            exit(0)


def get_tiles_dirs(tiles_root_dir, tiles_dirs, recursive, filter: Filter):

    tiles_dirs_all = []

    for tiles_dir in tiles_dirs:
        tiles_dir_path = linux_path(tiles_root_dir, tiles_dir)
        if recursive:
            tiles_dirs_ = [x[0] for x in os.walk(tiles_dir_path)]
        else:
            tiles_dirs_ = [
                linux_path(tiles_dir_path, x)
                for x in os.listdir(tiles_dir_path)
                if os.path.isdir(linux_path(tiles_dir_path, x))
            ]

        try:
            tiles_dirs_.remove(tiles_dir_path)
        except ValueError:
            pass

        tiles_dirs_ = filter.apply(tiles_dirs_)
        tiles_dirs_all += tiles_dirs_

    assert tiles_dirs_all, "no tiles dirs found"

    return tiles_dirs_all


def remove_common_suffix(models):
    if len(models) == 1:
        return "", models

    models_inv = [model[::-1] for model in models]
    cs = os.path.commonprefix(models_inv)
    if cs:
        models_inv = [model.replace(cs, "", 1) for model in models_inv]
        models = [model[::-1] for model in models_inv]
        cs = cs[::-1]
    return cs, models


def remove_common_prefix(models):
    if len(models) == 1:
        return "", models

    cp = os.path.commonprefix(models)
    if cp:
        models = [model.replace(cp, "", 1) for model in models]
    return cp, models


def check_wsi_files_and_slides(wsi_files, tiles_dirs):
    n_wsi_files = len(wsi_files)
    n_tiles_dirs = len(tiles_dirs)

    wsi_file_names = [path_to_name(wsi_file) for wsi_file in wsi_files]
    tiles_dir_names = [path_to_name(tiles_dir) for tiles_dir in tiles_dirs]

    if n_wsi_files != n_tiles_dirs:
        if n_wsi_files > n_tiles_dirs:
            unmatched_wsi_files = [
                wsi_file
                for wsi_file, wsi_file_name in zip(wsi_files, wsi_file_names, strict=True)
                if wsi_file_name not in tiles_dir_names
            ]
            print(f"unmatched_wsi_files: {to_str(unmatched_wsi_files)}")
        else:
            unmatched_tiles_dirs = [
                tiles_dir
                for tiles_dir, tiles_dir_name in zip(tiles_dirs, tiles_dir_names, strict=True)
                if tiles_dir_name not in wsi_file_names
            ]
            print(f"unmatched_tiles_dirs: {to_str(unmatched_tiles_dirs)}")
        raise AssertionError(
            f"mismatch between n_wsi_files ({n_wsi_files}) and n_tiles_dirs ({n_tiles_dirs})"
        )
    assert all(
        wsi_file_name == tiles_dir_name
        for wsi_file_name, tiles_dir_name in zip(wsi_file_names, tiles_dir_names, strict=True)
    ), "mismatch between one or more wsi_file and tiles_dir names"

    return n_wsi_files, wsi_file_names


def draw_geom_to_mask(geom, mask, color):
    if isinstance(color, (list, tuple))
    bkg_color = [0, ]*len(color)
    coords = np.array(geom.exterior.coords, dtype=np.int32)
    cv2.fillPoly(mask, [coords], color=color)
    for interior in geom.interiors:
        hole = np.array(interior.coords, dtype=np.int32)
        cv2.fillPoly(mask, [hole], color=0)


def draw_geom_to_semantic_mask(geom, sem_mask, col_id):
    coords = np.array(geom.exterior.coords, dtype=np.int32)
    cv2.fillPoly(sem_mask, [coords], color=col_id)
    for interior in geom.interiors:
        hole = np.array(interior.coords, dtype=np.int32)
        cv2.fillPoly(sem_mask, [hole], color=0)


def get_wsi_files(wsi_dir_path, wsi_exts, recursive, filter: Filter):
    if recursive:
        wsi_file_gen = [
            [
                linux_path(dirpath, f)
                for f in filenames
                if os.path.splitext(f.lower())[1] in wsi_exts
            ]
            for (dirpath, dirnames, filenames) in os.walk(wsi_dir_path, followlinks=True)
        ]
        all_wsi_files = [item for sublist in wsi_file_gen for item in sublist]
    else:
        all_wsi_files = [
            linux_path(wsi_dir_path, f)
            for f in os.listdir(wsi_dir_path)
            if os.path.splitext(f.lower())[1] in wsi_exts
        ]

    assert all_wsi_files, f"no wsi files found in {wsi_dir_path}"

    wsi_files = filter.apply(all_wsi_files)

    assert wsi_files, "no filtered wsi files left"

    return wsi_files


def path_to_id(path_):
    return extract_int_from_str(path_to_name(path_))


def is_date(filename, date_fmt):
    # print(f"filename: {filename}")
    try:
        datetime.strptime(filename, date_fmt)
    except ValueError as e:
        # print(f"not date: {e}")
        return False
    # print("is date")
    return True


def path_to_parent(path_):
    return os.path.dirname(path_)


def path_to_name(path_, remove_ext=True):
    file_name = os.path.basename(path_)
    if remove_ext:
        file_name = file_name.split(os.extsep)[0]

    return file_name


def get_id_from_name(id_to_name, name, add_missing=True):
    label_ids = [k for k, v in id_to_name.items() if v == name]
    if not label_ids:
        if not add_missing:
            raise AssertionError(f"label {name} not found")
        max_label_id = max(id_to_name.keys())
        label_id = max_label_id + 1
        id_to_name[label_id] = name
    else:
        assert len(label_ids) == 1, f"multple IDs found for {name}: {label_ids}"
        label_id = label_ids[0]
    return label_id


def extract_int_from_str(str_):
    int_substr = "".join(k for k in str_ if k.isdigit())
    if int_substr:
        return int(int_substr)
    return str_


def get_template_qupath() -> dict:
    template_polygon = {
        "type": "Feature",
        "id": "TODO",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [],
            ],
        },
        "properties": {
            # "objectType": "annotation",
            "area": 0,
            "objectType": "detection",
            # "measurements": [],
            "classification": {"name": "TODO", "color": []},
        },
    }
    return template_polygon


def cell_bbox_to_qupath_contour(cell_bbox):
    x1, y1, x2, y2 = map(int, cell_bbox)
    contour = [
        [x1, y1],
        [x2, y1],
        [x2, y2],
        [x1, y2],
        [x1, y1],
    ]
    return contour


def cell_mask_to_qupath_contour(cell_mask, cell_bbox):
    cell_mask_uint8 = cell_mask.astype(np.uint8) * 255

    # cell_mask_vis = resize_ar(cell_mask_uint8, max=500)
    # cv2.imshow("cell_mask_vis", cell_mask_vis)
    # cv2.waitKey(0)

    contour_raw = cv2.findContours(cell_mask_uint8, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_sorted = sorted(list(contour_raw[0]), key=lambda x: x.size, reverse=True)
    contour = np.squeeze(contours_sorted[0].astype("int32"))

    # contour_cv = to_contour_cv(cell_mask_uint8)
    # contour_ski = to_contour(cell_mask_uint8)

    if contour.size < 6:
        """a valid polygon must be at least a triangle"""
        return None

    contour[:, 0] += cell_bbox[0]
    contour[:, 1] += cell_bbox[1]

    contour = contour.tolist()

    contour.append(contour[0])

    return contour


def save_cells_as_qupath_geojson(
    cell_list, out_path, label_map, min_area, chunk_size=0, output_wsi_name=None
):

    features = []
    n_skipped = 0
    n_deleted = 0
    # cell_type_to_count = {cell_type: 0 for cell_type in self.label_map.keys()}
    pbar = tqdm(cell_list)
    for cell in pbar:
        if cell["to_delete"]:
            n_deleted += 1
            continue

        cell_area = cell["area"]
        if cell_area < min_area:
            n_skipped += 1
            continue

        cell_geojson_object = get_template_qupath()

        # cell_geojson_object["id"] = str(uuid.uuid4())
        cell_geojson_object["id"] = cell["id"]

        cell_type = cell["type"]
        cell_name = label_map[cell_type]
        cell_bbox = cell["wsi_bbox"]

        cell_mask = cell["mask"]

        if cell_mask is None:
            contour = cell_bbox_to_qupath_contour(cell_bbox)
        else:
            if isinstance(cell_mask, list):
                cell_mask = np.asarray(cell_mask, dtype=bool)

            contour = cell_mask_to_qupath_contour(cell_mask, cell_bbox)
            if contour is None:
                n_skipped += 1
                continue

        cell_geojson_object["geometry"]["coordinates"] = [
            contour,
        ]

        geom = shapely.geometry.shape(cell_geojson_object["geometry"])

        if not geom.is_valid:
            # shapely.is_valid_reason(shapely.geometry.Polygon(contour))
            # print(
            #     f"skipping cell with invalid geometry"
            # )
            n_skipped += 1
            continue

        # cell_geojson_object["properties"]["area"] = int(cell["area"])
        cell_geojson_object["properties"]["classification"]["name"] = cell_name
        cell_geojson_object["properties"]["classification"]["color"] = COLOR_DICT_CELLS[cell_name]

        features.append(cell_geojson_object)

        pbar.set_description(f"save_cells_as_qupath: deleted: {n_deleted} skipped: {n_skipped}")

    save_geojson_as_chunks(features, chunk_size, out_path, output_wsi_name)
    return features


def load_annotations_from_qupath_geojson(ann_path, ann_ext=".geojson.gz", verbose=True):
    features = load_geojson_as_chunks(ann_path, ann_ext, verbose=verbose)
    n_features = len(features)

    assert n_features > 0, "no objects found in geojson"

    polygons = []
    bboxes = []
    if verbose:
        pbar = tqdm(features, total=n_features)
    else:
        pbar = features

    for feat_id, feat in enumerate(pbar):

        if verbose:
            pbar.set_description(f"load_annotations_from_qupath_geojson")

        feat_properties = feat["properties"]
        if feat_properties["objectType"] != "annotation":
            continue

        geometry = feat["geometry"]

        geom = shapely.geometry.shape(geometry)

        sub_parts = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
        for poly in sub_parts:
            coords = np.array(poly.exterior.coords, dtype=np.float32)
            xs = coords[:, 0]
            ys = coords[:, 1]

            min_x, max_x = np.amin(xs), np.amax(xs)
            min_y, max_y = np.amin(ys), np.amax(ys)

            bboxes.append(np.asarray([min_x, min_y, max_x, max_y]))
            polygons.append(coords)

    return polygons, bboxes


def load_detections_from_qupath_geojson(
    ann_path, labels, ignore_invalid_label=True, ann_ext=".geojson.gz"
):
    features = load_geojson_as_chunks(ann_path, ann_ext)
    n_features = len(features)

    assert n_features > 0, "no objects found"

    polygons = []
    feats = []
    classes = []
    invalid_label = 0
    no_class = 0
    multi_poly = 0
    pbar = tqdm(features, total=n_features)
    for feat_id, feat in enumerate(pbar):

        pbar.set_description(
            f"filtering objs: invalid_label: {invalid_label} multi_poly: {multi_poly} no_class: {no_class}"
        )

        feat_properties = feat["properties"]
        if feat_properties["objectType"] != "detection":
            no_class += 1
            continue

        if "classification" not in feat_properties:
            no_class += 1
            continue

        class_info = feat_properties["classification"]
        try:
            class_name = class_info["name"]
        except KeyError:
            """if geojson is directly exported from qupath, a nucleus can have multiple labels if it is contained inside one or more labeled regions"""
            all_classes = class_info["names"]
            matching_classes = [cls for cls in all_classes if cls in labels]

            if not matching_classes:
                if ignore_invalid_label:
                    invalid_label += 1
                    continue
                raise AssertionError(f"invalid label(s) found: {all_classes}")

            assert (
                len(matching_classes) == 1
            ), f"multiple matching classes found: {matching_classes}"

            class_name = matching_classes[0]

        if class_name not in labels:
            if ignore_invalid_label:
                invalid_label += 1
                continue
            raise AssertionError(f"invalid label found: {class_name}")

        geometry = feat["geometry"]

        if geometry["type"] == "MultiPolygon":
            multi_poly += 1
            continue

        polygon = np.asarray(geometry["coordinates"][0])
        # polygon = shapely.geometry.shape(geometry)

        polygons.append(polygon)
        classes.append(class_name)
        feats.append(feat)

    return polygons, classes, feats


def load_geojson_as_chunks(ann_path, ann_ext=".geojson.gz", verbose=True):

    if ann_path.endswith(ann_ext):
        ann_paths = [
            ann_path,
        ]
        if verbose:
            print(f"loading annotations from {ann_path}")
    else:
        assert os.path.isdir(ann_path), f"invalid geojson directory: {ann_path}"
        if verbose:
            print(f"loading annotations from geojsons in {ann_path}")
        ann_paths = [k.path for k in os.scandir(ann_path) if k.name.endswith(ann_ext)]
        assert ann_paths, "no geojson files found"

    n_ann_paths = len(ann_paths)
    features = []
    for ann_path_id, ann_path_ in enumerate(ann_paths):
        if verbose and n_ann_paths > 1:
            print(f"\t{ann_path_id+1}/{len(ann_paths)}: {ann_path_}")
        with gzip.open(
            ann_path_,
            mode="rt",
            encoding="utf-8",
            # **compression_kwarg,
        ) as fid:
            # df = geopandas.read_file(fid, driver="geojson")
            features_ = geojson.loads(fid.read())
            if isinstance(features_, dict):
                features_ = features_["features"]
            features += features_
            # df = geopandas.GeoDataFrame.from_features(allobjects)

    assert features, "no objects found"

    # print(f"loaded {len(features)} objects")

    return features


def save_geojson_as_chunks(features, chunk_size, out_path, output_wsi_name=None):
    if chunk_size > 0:
        n_features = len(features)
        features_chunks = list(chunks(features, chunk_size))
        n_chunks = len(features_chunks)
        print(f"splitting {n_features} detections into {n_chunks} chunks")
    else:
        features_chunks = [
            features,
        ]
        n_chunks = 1

    if output_wsi_name is None:
        output_wsi_name = path_to_name(out_path)

    for chunk_id, chunk_features in enumerate(features_chunks):
        out_name = f"{output_wsi_name}"
        if n_chunks > 1:
            out_name = f"{out_name}_{int_to_padded_str(chunk_id)}"

        out_name = f"{out_name}.geojson.gz"

        chunk_out_path = str(Path(out_path) / out_name)
        print(f"\t{chunk_id+1} / {n_chunks}: {chunk_out_path}")
        compress_json.dump(chunk_features, chunk_out_path, json_kwargs=dict(indent=4))


def int_to_padded_str(num):
    if num < 1e2:
        num_str = f"{num:02d}"
    elif num < 1e3:
        num_str = f"{num:03d}"
    elif num < 1e4:
        num_str = f"{num:04d}"
    elif num < 1e5:
        num_str = f"{num:05d}"
    else:
        num_str = f"{num:06d}"
    return num_str


def google_sheet_test(time_fmt):
    import gspread
    import datetime

    gc = gspread.service_account()

    sh = gc.open("magee_test")
    worksheet = sh.get_worksheet(0)

    print(worksheet.get("A1"))
    print(worksheet.cell(1, 1).value)

    header_names = worksheet.row_values(1)

    accession_ids = worksheet.col_values(1)

    empty_row_id = len(accession_ids) + 1

    accession_col_id = header_names.index("accession_id") + 1
    status_col_id = header_names.index("status") + 1
    added_col_id = header_names.index("added") + 1
    modified_col_id = header_names.index("modified") + 1

    worksheet.update_cell(empty_row_id, accession_col_id, "MIS26-999993")
    worksheet.update_cell(empty_row_id, status_col_id, "waiting for annotation")

    timestamp = datetime.now().strftime(time_fmt)
    worksheet.update_cell(empty_row_id, added_col_id, timestamp)
    worksheet.update_cell(empty_row_id, modified_col_id, timestamp)


def init_logger(term_log_path):
    import logging

    log_format = "%(asctime)s %(levelname)-8s %(message)s"
    logger = logging.getLogger("")

    # log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # logging.basicConfig(
    #     format=log_format,
    #     level=logging.DEBUG,
    #     datefmt="%Y-%m-%d %H:%M:%S",
    #     handlers=[logging.FileHandler(term_log_path), logging.StreamHandler()],
    # )

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(log_format)
    term_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(term_log_path)
    term_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(term_handler)
    logger.addHandler(file_handler)

    return logger


def wait_for_file_to_finalize(filepath, wait_secs, verbose):
    file_stat = Path(filepath).stat()
    mod_t = datetime.fromtimestamp(file_stat.st_mtime)

    secs_since_last_mod = (datetime.now() - mod_t).total_seconds()
    if secs_since_last_mod > wait_secs:
        return

    file_name = path_to_name(filepath, remove_ext=False)

    if verbose:
        pbar = tqdm(desc=f"wait_for_file_to_finalize: {file_name} ({wait_secs} secs)")

    while True:
        first_size = os.path.getsize(filepath)
        time.sleep(wait_secs)
        second_size = os.path.getsize(filepath)

        if first_size == second_size:
            break

        if verbose:
            pbar.update(1)
