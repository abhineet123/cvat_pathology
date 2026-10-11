import os
import cv2
import numpy as np
import json

np.set_printoptions(legacy="1.25")

from tqdm import tqdm
from PIL import Image
from datetime import datetime

import compress_json
import urllib3
import itertools
import paramparse
import fiftyone as fo


from cvat_sdk import make_client
from cvat_sdk import masks

from cell_seg_utils import (
    CVATAuth,
    Filter,
    linux_path,
    hex_to_rgb,
    get_job_url,
    sleep_with_pbar,
    get_51_url,
    load_annotations_from_cache,
    save_annotations_to_cache,
)

# fo.close_app()
# print(fo.config)
# fo.config.default_app_port = 5252


class FiftyOneConfigs:
    @staticmethod
    def cellpose(dataset):
        try:
            dataset.default_group_slice = "cellpose"
            dataset.group_slice = "cellpose"
        except ValueError:
            pass
        except AttributeError:
            pass
        dataset.app_config.color_scheme.opacity = 0.18
        for field in dataset.app_config.color_scheme.fields:
            if field["path"] == "cellpose":
                field["fieldColor"] = "#009900"


class Params(paramparse.CFG):
    """
    :ivar delete_mode: Show the list of existing datasets (matching any filtering conditions if specified) to allow the user to delete one or more of them interactively
        delete_mode=2 would delete all the existing datasets non-interactively
    """

    def __init__(self):
        paramparse.CFG.__init__(self)

        self.auth = CVATAuth()
        self.filter = Filter()

        self.dataset_name = ""

        self.local = 0
        self.alpha = 0.25

        self.root_dir = "/data/PDL1-2026-Tiles"
        self.vis_dir = "vis"
        self.directory = ""
        self.recursive = 0

        self.project_name = ""
        self.chunk_id = -1
        self.delete_mode = 0
        self.config_db = ""

        self.grouped = 0
        self.persistent = 1
        self.ignore_name_failure = 0

        self.address = ""
        self.permanent = 0
        self.port = 0
        self.remote = 0
        self.start_app = 0
        self.ignore_invalid = 0

        self.start_dir_id = 0
        self.end_dir_id = -1

        self.start_model_id = 0
        self.end_model_id = -1

        self.start_task_id = 0
        self.end_task_id = -1

        self.start_frame_id = 0
        self.end_frame_id = -1

        self.time_suffix = 0
        self.load_existing = 0
        self.remove_existing = 0
        self.append_existing = 0

        self.save_metadata = 1
        self.metadata_root = ".fiftyone"
        self.host_url = ""

        self.excp_wait_t = 120
        self.verbose = 1
        self.check_files = 0
        self.load_from_cache = 0
        self.save_to_cache = 0
        self.max_samples = 0

        self.opacity = 0.25

        self.multi_labels = []
        self.model_suffixes = []
        self.cols = [
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#f1a66d",
            "#ff00ff",
            "#00ffff",
            "#ffff00",
            "#228b22",
        ]


def get_datasets(filter: Filter, allow_empty=True):
    dataset_names = list(fo.list_datasets())
    dataset_names = filter.apply(dataset_names)
    dataset_names.sort()
    if not allow_empty:
        assert dataset_names, "no valid datasets found"

    return dataset_names


def start_app(params: Params, allow_empty=False):
    app_config = fo.app_config.copy()
    app_config.show_confidence = False
    app_config.show_label = False
    app_config.show_tooltip = False
    app_config.show_index = False
    # print(app_config)

    dataset_names = get_datasets(params.filter, allow_empty=allow_empty)

    app_params = dict(remote=params.remote, config=app_config)
    if params.address:
        app_params.update(dict(address=params.address))
    if params.port:
        app_params.update(dict(port=params.port))

    if dataset_names:
        datasets_str = "\n".join(dataset_names)
        print(f"dataset_names:\n{datasets_str}")
        app_params["dataset"] = fo.load_dataset(dataset_names[0])

    session = fo.launch_app(**app_params)
    wait_t = -1 if params.permanent else 0
    session.wait(wait_t)
    session.close()


def config_datasets(filter: Filter, config_nane):
    # config_json_path = linux_path("cfg", "fiftyone", f"{config_nane}.json")
    # with open(config_json_path, "r") as f:
    #     config_dict = json.load(f)
    config_func = getattr(FiftyOneConfigs, config_nane)
    dataset_names = get_datasets(filter)
    for i, dataset_name in enumerate(dataset_names):
        print(f"{dataset_name}")
        dataset = fo.load_dataset(dataset_name)

        config_func(dataset)

        # app_config_dict = dataset.app_config.to_dict()
        # dataset.app_config.from_json(config_json_path)
        # app_config_dict.update(config_dict)
        # dataset.app_config.from_dict(app_config_dict)
        # app_config_ds2 = dataset.app_config
        dataset.save()


def delete_datasets(filter: Filter, delete_all=False):
    while True:
        dataset_names = get_datasets(filter)
        if not dataset_names:
            print("No matching datasets found to delete\n")
            break

        dataset_counts = []
        for i, dataset_name in enumerate(dataset_names):
            dataset = fo.load_dataset(dataset_name)
            dataset_stats = dataset.stats()
            # print(dataset.app_config)
            dataset_samples_count = dataset_stats["samples_count"]
            print(f"{i}: {dataset_name}\t{dataset_samples_count}")
            dataset_counts.append(dataset_samples_count)

        if delete_all:
            print("deleting all datasets\n")
            delete_ids = list(range(len(dataset_names)))
        else:
            k = input("Select datasets to delete (-1 for all). Enter to exit.\n")
            if not k:
                break
            # delete_ids = list(map(int, k.split(",")))
            if k in ["__empty__", "__e__"]:
                delete_ids = [
                    i for i, dataset_count in enumerate(dataset_counts) if dataset_count == 0
                ]
            else:
                delete_ids = paramparse.str_to_tuple_multi(k)
                if len(delete_ids) == 1 and delete_ids[0] == -1:
                    delete_all = 1
                    print("deleting all datasets\n")
                    delete_ids = list(range(len(dataset_names)))

        for delete_id in delete_ids:
            dataset_name = dataset_names[delete_id]
            dataset_count = dataset_counts[delete_id]
            print(f"deleting dataset {delete_id}: {dataset_name} (count: {dataset_count})")
            fo.delete_dataset(dataset_name)

        if delete_all:
            break


def main():
    params: Params = paramparse.process(Params)
    run(params)


def run(params: Params, cvat_info=None):

    params.cols = [col if col.startswith("#") else f"#{col}" for col in params.cols]

    if params.local:
        print("running in local output mode")
        all_rgb_cols = list(itertools.product(range(256), repeat=3))
        # rgb_cols_to_id = {rgb_col: i for i, rgb_col in enumerate(all_rgb_cols)}
    else:
        if params.delete_mode:
            delete_datasets(params.filter, delete_all=params.delete_mode == 2)
            return
        if params.config_db:
            config_datasets(params.filter, params.config_db)
            return
        if params.start_app == 2:
            start_app(params, allow_empty=True)
            return

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

    model_suffixes = []
    all_labels = []
    for model_suffix in params.model_suffixes:
        if model_suffix == "multi":
            assert (
                params.multi_labels
            ), "at least one label must be provided to extract annotations from multi-label task"
            labels_str = "_".join(params.multi_labels)
            model_suffixes.append(f"multi-{labels_str}")
            all_labels += list(params.multi_labels)
        else:
            model_suffixes.append(model_suffix)
            all_labels.append(model_suffix)

    models_suffix = "_".join(model_suffixes)

    vis_dataset_name = params.dataset_name

    if not vis_dataset_name:
        vis_dataset_name = f"{params.project_name}-{models_suffix}"
        if params.filter.iall:
            include_suffix = "_".join(params.filter.iall)
            vis_dataset_name = f"{vis_dataset_name}-{include_suffix}"

        # if params.chunk_id == 0:
        # vis_dataset_name = f"{vis_dataset_name}-all_chunks"

        if params.chunk_id > 0:
            vis_dataset_name = f"{vis_dataset_name}-chunk_{params.chunk_id:02d}"

        if params.grouped:
            vis_dataset_name = f"{vis_dataset_name}-grouped"

        if params.time_suffix:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            vis_dataset_name = f"{vis_dataset_name}-{timestamp}"

    dataset_names = get_datasets(params.filter)
    dataset_loaded = False
    if vis_dataset_name in dataset_names:
        if params.load_existing:
            print(f"loading existing dataset: {vis_dataset_name}\n")
            dataset = fo.load_dataset(vis_dataset_name)
            dataset_loaded = True
        elif params.remove_existing:
            print(f"deleting existing dataset: {vis_dataset_name}\n")
            fo.delete_dataset(vis_dataset_name)
        else:
            raise AssertionError(f"existing dataset found: {vis_dataset_name}")

    while True:
        try:
            client = make_client(**client_cfg)
        except (urllib3.exceptions.MaxRetryError,) as e:
            print(
                f"\n\nclient creation failed:\n{e}\nWaiting {params.excp_wait_t} seconds before trying again\n\n"
            )
            sleep_with_pbar(params.excp_wait_t)
            continue
        else:
            break

    if cvat_info is None:
        print("getting cvat tasks info...")
        tasks_dict = [task.__dict__ for task in client.tasks.list()]
        print("getting cvat projects info...")
        projects_dict = [project.__dict__ for project in client.projects.list()]
    else:
        tasks_dict, projects_dict = cvat_info

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
    # project_name_to_dict = {
    #     project["_model"]["name"]: project["_model"] for project in projects_dict
    # }
    if not dataset_loaded:
        print(f"\ncreating vis dataset: {vis_dataset_name}\n")
        if params.local:
            vis_root_dir_path = linux_path(params.root_dir, params.vis_dir, vis_dataset_name)
            os.makedirs(vis_root_dir_path, exist_ok=True)
        else:
            try:
                dataset = fo.Dataset(vis_dataset_name, persistent=params.persistent)
            except ValueError as e:
                if params.ignore_name_failure:
                    print(e)
                    print("using auto-generated dataset name")
                    dataset = fo.Dataset()
                else:
                    raise e

            app_config_ds = dataset.app_config
            app_config_ds.color_scheme = fo.ColorScheme(
                color_by="field",
                opacity=params.opacity,
                fields=[
                    {
                        "path": label_name,
                        "fieldColor": params.cols[label_id],
                    }
                    for label_id, label_name in enumerate(all_labels)
                ],
            )

            # app_config_global = fo.DatasetAppConfig
            # sidebar_groups = app_config_global.default_sidebar_groups(dataset)
            # active_fields = app_config_global.default_active_fields(dataset)

            if params.grouped:
                dataset.add_group_field("model")

    image_exts = ["jpg", "jpeg", "bmp", "png", "tif", "webp"]

    task_name_to_51_dataset = {}

    for subdir_id, subdir in enumerate(subdirs):

        if subdir_id < params.start_dir_id:
            if params.verbose:
                print(f"\nskipping subdir {subdir_id+1}/{n_subdirs}: {subdir}\n")
            continue

        if subdir_id > params.end_dir_id >= 0:
            if params.verbose:
                print(f"\nskipping subdirs with id > {params.end_dir_id}\n")
            break

        if params.verbose:
            print(f"\nsubdir {subdir_id+1}/{n_subdirs}: {subdir}\n")

        image_paths = [
            os.path.join(subdir, k)
            for k in os.listdir(subdir)
            if any(k.lower().endswith(f".{_ext}") for _ext in image_exts)
        ]

        if not image_paths:
            print(f"Skipping subdir with no images: {subdir}")
            continue

        task_suffix = os.path.relpath(subdir, dir_path)

        samples = []
        file_path_to_group = {}
        file_path_to_sample = {}
        n_model_suffixes = len(params.model_suffixes)
        for model_id, model_suffix in enumerate(params.model_suffixes):

            if model_id < params.start_model_id:
                if params.verbose:
                    print(f"\nskipping model {model_id+1}/{n_model_suffixes}: {model_suffix}\n")
                continue

            if model_id > params.end_model_id >= 0:
                if params.verbose:
                    print(f"\nskipping models with id > {params.end_model_id}\n")
                break

            multi_label_task = False
            if model_suffix == "multi":
                multi_label_task = True

            if params.local:
                model_color_rgb = hex_to_rgb(params.cols[model_id])
                vis_mask_dir_path = linux_path(vis_root_dir_path, f"masks-{model_suffix}")
                vis_img_dir_path = linux_path(vis_root_dir_path, f"overlaid-{model_suffix}")

                # if os.path.exists(vis_img_dir_path) and os.path.exists(vis_mask_dir_path):
                # print(f"skipping already existing vis_dir_path: {vis_dir_path}")
                # continue

                os.makedirs(vis_mask_dir_path, exist_ok=True)
                os.makedirs(vis_img_dir_path, exist_ok=True)

            project_name = f"{params.project_name}-{model_suffix}"

            if project_name not in project_name_to_id:
                if params.ignore_invalid:
                    print(f"Skipping invalid project: {project_name}")
                    continue
                else:
                    raise AssertionError(f"invalid project_name: {project_name}")

            # project_id = project_name_to_id[project_name]
            # project_dict = project_name_to_dict[project_name]

            task_name_ = f"{project_name}-{task_suffix}"

            if params.chunk_id == 0:
                task_name_templ = f"{task_name_}-chunk_"
                task_names = [k for k in task_name_to_id.keys() if k.startswith(task_name_templ)]
                if params.verbose:
                    print(f"processing tasks for {len(task_names)} chunks")
            else:
                if params.chunk_id > 0:
                    task_name_ = f"{task_name_}-chunk_{params.chunk_id:02d}"
                task_names = [
                    task_name_,
                ]

            n_tasks = len(task_names)
            for task_name_id, task_name in enumerate(task_names):
                if task_name_id < params.start_task_id:
                    if params.verbose:
                        print(f"\nskipping task {task_name_id+1}/{n_tasks}: {task_name}\n")
                    continue

                if task_name_id > params.end_task_id >= 0:
                    if params.verbose:
                        print(f"\nskipping tasks with id > {params.end_task_id}\n")
                    break

                if task_name not in task_name_to_id:
                    if params.ignore_invalid:
                        print(f"Skipping invalid task: {task_name}")
                        continue
                    else:
                        raise AssertionError(f"invalid task_name: {task_name}")

                task_name_to_51_dataset[task_name] = vis_dataset_name

                if dataset_loaded and not params.append_existing:
                    continue

                # task_obj = task_name_to_obj[task_name]
                # task_dict = task_obj["_model"]

                task_id = task_name_to_id[task_name]
                task = client.tasks.retrieve(task_id)

                if params.save_metadata:

                    model_job_url = get_job_url(client, task, task_name)

                    ensemble_task_name = task_name.replace(model_suffix, "ensemble")
                    ensemble_task_id = task_name_to_id[ensemble_task_name]
                    ensemble_task = client.tasks.retrieve(ensemble_task_id)

                    ensemble_job_url = get_job_url(client, ensemble_task, ensemble_task_name)

                labels = task.get_labels()

                label_id_to_name = {label["id"]: label["name"] for label in labels}
                label_name_to_id = {label["name"]: label["id"] for label in labels}

                frames_info = task.get_frames_info()

                if params.load_from_cache:
                    from collections import defaultdict

                    shapes = defaultdict(list)
                    if multi_label_task:
                        for label_name in params.multi_labels:
                            label_shapes = load_annotations_from_cache(
                                project_name, label_name, task_name
                            )
                            for k, v in label_shapes.items():
                                shapes[k] += v
                    else:
                        shapes = load_annotations_from_cache(project_name, model_suffix, task_name)

                    # print()
                else:
                    print(f"{task_name}: get_annotations...")
                    annotations = task.get_annotations()

                    shapes = annotations["shapes"]

                    if multi_label_task:
                        multi_label_ids = [
                            label_name_to_id[label_name] for label_name in params.multi_labels
                        ]
                        shapes = [shape for shape in shapes if shape["label_id"] in multi_label_ids]

                    if params.save_to_cache:
                        frame_name_to_shapes = {}
                        if multi_label_task:
                            for label_name in params.multi_labels:
                                frame_name_to_shapes[label_name] = {}

                n_model_objs_all = 0

                pbar = tqdm(
                    enumerate(frames_info),
                    total=len(frames_info),
                )

                for frame_id, frame_info in pbar:

                    if frame_id < params.start_frame_id:
                        continue

                    if params.end_frame_id >= 0 and frame_id > params.end_frame_id:
                        break

                    frame_dict = frame_info.to_dict()
                    frame_w, frame_h = frame_dict["width"], frame_dict["height"]

                    frame_name = frame_dict["name"]
                    frame_path = linux_path(subdir, frame_name)
                    if params.check_files:
                        assert os.path.exists(frame_path), f"nonexistent frame_path: {frame_path}"

                    if params.load_from_cache:
                        frame_shapes = shapes[frame_name]
                    else:
                        frame_shapes = [
                            shape.to_dict() for shape in shapes if shape["frame"] == frame_id
                        ]
                        if params.save_to_cache:
                            if multi_label_task:
                                for label_name in params.multi_labels:
                                    frame_name_to_shapes[label_name][frame_name] = []
                                for shape in frame_shapes:
                                    label_name = label_id_to_name[shape["label_id"]]
                                    frame_name_to_shapes[label_name][frame_name].append(shape)

                            else:
                                frame_name_to_shapes[frame_name] = frame_shapes

                    # frame_points = [shape["points"] for shape in frame_shapes]
                    # frame_bbs = [points[-4:] for points in frame_points]
                    # frame_areas = [(bb[2] - bb[0]) * (bb[3] - bb[1]) for bb in frame_bbs]
                    # frame_points_len = [len(points) for points in frame_points]

                    if params.local:
                        frame_img = Image.open(frame_path)

                        frame_img_np = np.asarray(frame_img)
                        assert frame_img_np.shape[:2] == (
                            frame_h,
                            frame_w,
                        ), "frame size mismatch"

                        # frame_mask = np.zeros((frame_h, frame_w), dtype=np.int32)
                        frame_mask = np.zeros_like(frame_img_np)
                    else:
                        if params.grouped:
                            try:
                                group = file_path_to_group[frame_path]
                            except KeyError:
                                group = file_path_to_group[frame_path] = fo.Group()

                            if multi_label_task:
                                label_to_sample = {}
                                for label_name in params.multi_labels:
                                    sample_ = fo.Sample(
                                        filepath=frame_path, model=group.element(label_name)
                                    )
                                    samples.append(sample_)
                                    label_to_sample[label_name] = sample_
                                sample = None
                            else:
                                sample = fo.Sample(
                                    filepath=frame_path, model=group.element(model_suffix)
                                )
                                samples.append(sample)
                        else:
                            try:
                                sample = file_path_to_sample[frame_path]
                            except KeyError:
                                sample = file_path_to_sample[frame_path] = fo.Sample(
                                    filepath=frame_path
                                )
                                samples.append(sample)

                        if params.save_metadata:
                            model_url = f"{model_job_url}?frame={frame_id}"
                            ensemble_url = f"{ensemble_job_url}?frame={frame_id}"

                            model_tag = f"{model_suffix}: {model_url}"
                            ensemble_tag = f"ensemble: {ensemble_url}"

                            if params.grouped and multi_label_task:
                                for sample_ in label_to_sample.values():
                                    if model_tag not in sample_.tags:
                                        sample_.tags.append(model_tag)
                                    if ensemble_tag not in sample_.tags:
                                        sample_.tags.append(ensemble_tag)
                            else:
                                if model_tag not in sample.tags:
                                    sample.tags.append(model_tag)
                                if ensemble_tag not in sample.tags:
                                    sample.tags.append(ensemble_tag)

                    detections = label_to_detections = None
                    if multi_label_task:
                        label_to_detections = {label_name: [] for label_name in params.multi_labels}
                    else:
                        detections = []

                    shape_id = 0
                    shape_ids = []
                    for shape in frame_shapes:
                        pts = shape["points"]
                        obj_mask = masks.decode_mask(pts, image_width=frame_w, image_height=frame_h)
                        ys, xs = np.nonzero(obj_mask)
                        if ys.size == 0:
                            continue
                        shape_id += 1

                        shape_ids.append(shape_id)

                        if params.local:
                            # frame_mask[obj_mask] = shape_id
                            frame_mask[obj_mask] = all_rgb_cols[shape_id]
                            vis_mask = np.zeros_like(frame_img_np)
                            vis_mask[obj_mask] = model_color_rgb

                            frame_blended = np.asarray(
                                Image.blend(frame_img, Image.fromarray(vis_mask), params.alpha)
                            )
                            obj_mask_rgb = np.stack((obj_mask,) * 3, axis=2)
                            frame_img_np = np.where(obj_mask_rgb, frame_blended, frame_img_np)
                        else:
                            xmin, ymin, xmax, ymax = (
                                np.amin(xs),
                                np.amin(ys),
                                np.amax(xs),
                                np.amax(ys),
                            )

                            obj_mask_cropped = obj_mask[ymin : ymax + 1, xmin : xmax + 1]
                            xmin, ymin, xmax, ymax = (
                                float(xmin) / frame_w,
                                float(ymin) / frame_h,
                                float(xmax) / frame_w,
                                float(ymax) / frame_h,
                            )
                            bb_w, bb_h = xmax - xmin, ymax - ymin

                            label_id = shape["label_id"]
                            label = label_id_to_name[label_id]
                            detection = fo.Detection(
                                label="nucleus" if multi_label_task else label,
                                bounding_box=[xmin, ymin, bb_w, bb_h],
                                mask=obj_mask_cropped,
                            )
                            if multi_label_task:
                                label_to_detections[label].append(detection)
                            else:
                                detections.append(detection)

                    n_frame_objs = shape_id
                    # n_frame_objs = len(frame_shapes)
                    n_model_objs_all += n_frame_objs
                    pbar.set_description(
                        f"task {task_name_id+1}/{n_tasks} {task_name}: {model_suffix} ({n_model_objs_all} objs)"
                    )

                    if params.local:
                        vis_img_path = linux_path(vis_img_dir_path, frame_name)
                        Image.fromarray(frame_img_np).save(vis_img_path)
                        # frame_img.save(vis_img_path)

                        # cv2.imshow("frame_img_np", frame_img_np)
                        # cv2.waitKey(0)

                        mask_name = os.path.splitext(frame_name)[0] + ".png"
                        vis_mask_path = linux_path(vis_mask_dir_path, mask_name)

                        mask_pil = Image.fromarray(frame_mask)
                        mask_pil.save(vis_mask_path)
                        # cv2.imwrite(vis_mask_path, frame_mask)

                        # rec_mask = np.asarray(Image.open(vis_mask_path))
                        # unique_rgb_vals = np.unique(rec_mask.reshape(-1, rec_mask.shape[2]), axis=0)
                        # unique_ids = list(
                        #     rgb_cols_to_id[tuple(rgb_val)] for rgb_val in unique_rgb_vals
                        # )
                        # unique_ids.remove(0)
                        # assert unique_ids == shape_ids, "unique_ids-shape_ids mismatch"
                        # print()

                    else:
                        if multi_label_task:
                            for label_name in params.multi_labels:
                                if params.grouped:
                                    label_to_sample[label_name][label_name] = fo.Detections(
                                        detections=label_to_detections[label_name]
                                    )
                                else:
                                    sample[label_name] = fo.Detections(
                                        detections=label_to_detections[label_name]
                                    )
                        else:
                            # if params.grouped:
                            #     sample["detections"] = fo.Detections(detections=detections)
                            # else:
                            sample[model_suffix] = fo.Detections(detections=detections)

                if params.save_to_cache:
                    if multi_label_task:
                        for label_name in params.multi_labels:
                            label_shapes = frame_name_to_shapes[label_name]
                            save_annotations_to_cache(
                                label_shapes, project_name, label_name, task_name
                            )
                    else:
                        save_annotations_to_cache(
                            frame_name_to_shapes, project_name, model_suffix, task_name
                        )

                if (
                    (not params.local)
                    and (params.grouped or n_model_suffixes == 1)
                    and (len(samples) > params.max_samples > 0)
                ):
                    """overlaid samples need to be reused across models so we cannot remove them here"""
                    dataset.add_samples(samples)
                    samples = []

        if not params.local:
            dataset.add_samples(samples)
        # break

    # for sample in tqdm(dataset, desc="url_to_tags"):
    #     print()
    #     sample.tags = [task_url, ensemble_task_url]

    client.close()

    if params.save_metadata:

        # dataset_stats = dataset.stats()
        json_kwargs = dict(indent=4)
        if params.grouped:
            metadata_dir = linux_path(params.metadata_root, "grouped")
        else:
            metadata_dir = linux_path(params.metadata_root, "overlaid")
        os.makedirs(metadata_dir, exist_ok=True)

        task_name_to_dataset_path = linux_path(metadata_dir, "task_name_to_dataset.json.gz")
        print(f"saving task_name_to_dataset to {task_name_to_dataset_path}")

        if os.path.exists(task_name_to_dataset_path):
            task_name_to_dataset_: dict = compress_json.load(task_name_to_dataset_path)
            task_name_to_dataset_.update(task_name_to_51_dataset)
            task_name_to_51_dataset = task_name_to_dataset_

        compress_json.dump(
            task_name_to_51_dataset, task_name_to_dataset_path, json_kwargs=json_kwargs
        )

        db_metadata_dir = linux_path(metadata_dir, vis_dataset_name)
        os.makedirs(db_metadata_dir, exist_ok=True)

        if not params.host_url:
            params.host_url = get_51_url(grouped=params.grouped)
            print(f"using fiftyone host_url: {params.host_url}")

        filename_to_url = {}
        # filename_to_info = {}
        for sample in tqdm(dataset, desc="filename_to_url"):
            filename = os.path.basename(str(sample.filepath))
            fiftyone_db_url = f"{params.host_url}/datasets/{vis_dataset_name}"
            if params.grouped:
                fiftyone_file_url = (
                    f"{fiftyone_db_url}?slice={sample.model.name}&groupId={sample.model.id}"
                )
            else:
                fiftyone_file_url = f"{fiftyone_db_url}?id={sample.id}"

            filename_to_url[filename] = fiftyone_file_url

            # sample_dict = sample.to_dict()
            # filename_to_info[filename] = sample_dict

        filename_to_url_path = linux_path(db_metadata_dir, "filename_to_url.json.gz")
        print(f"saving filename_to_url to {filename_to_url_path}")

        compress_json.dump(filename_to_url, filename_to_url_path, json_kwargs=json_kwargs)

    if not params.local and params.start_app:
        app_params = dict(dataset=dataset, remote=params.remote)
        if params.port:
            app_params.update(dict(port=params.port))
        session = fo.launch_app(**app_params)

        session.wait(0)
        session.close()


if __name__ == "__main__":
    main()
