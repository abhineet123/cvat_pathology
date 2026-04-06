import os
import cv2
import numpy as np

np.set_printoptions(legacy="1.25")

from tqdm import tqdm
from PIL import Image
from datetime import datetime

import itertools
import paramparse
import fiftyone as fo


from cvat_sdk import make_client
from cvat_sdk import masks

from cell_seg_utils import CVATAuth, Filter, linux_path, hex_to_rgb

# fo.close_app()
# print(fo.config)
# fo.config.default_app_port = 5252


class Params(paramparse.CFG):
    def __init__(self):
        paramparse.CFG.__init__(self)

        self.auth = CVATAuth()
        self.filter = Filter()

        self.local = 0
        self.alpha = 0.25

        self.root_dir = "/data/PDL1-2026-Tiles"
        self.vis_dir = "vis"
        self.directory = ""
        self.recursive = 0

        self.project_name = ""
        self.chunk_id = -1
        self.delete_mode = 0

        self.grouped = 0
        self.persistent = 1

        self.address = ""
        self.permanent = 0
        self.port = 0
        self.remote = 0
        self.start_app = 0
        self.ignore_invalid = 0

        self.model_suffixes = []
        self.model_colors = [
            "#ff0000",
            "#00ff00",
            "#0000ff",
            "#f1a66d",
        ]


def get_datasets(filter: Filter, allow_empty=True):
    dataset_names = list(fo.list_datasets())
    dataset_names = filter.apply(dataset_names)
    dataset_names.sort()
    if not allow_empty:
        assert dataset_names, "no valid datasets found"

    return dataset_names


def main():
    params: Params = paramparse.process(Params)

    all_rgb_cols = list(itertools.product(range(256), repeat=3))
    rgb_cols_to_id = {rgb_col: i for i, rgb_col in enumerate(all_rgb_cols)}

    if params.local:
        print("running in local output mode")
    else:
        if params.delete_mode:
            while True:
                dataset_names = get_datasets(params.filter)
                for i, dataset_name in enumerate(dataset_names):
                    dataset = fo.load_dataset(dataset_name)
                    dataset_stats = dataset.stats()
                    # print(dataset.app_config)
                    dataset_samples_count = dataset_stats["samples_count"]
                    print(f"{i}: {dataset_name}\t{dataset_samples_count}")
                k = input("Select datasets to delete. Enter to exit.\n")
                if not k:
                    break
                delete_ids = map(int, k.split(","))
                for delete_id in delete_ids:
                    dataset_name = dataset_names[delete_id]
                    print(f"deleting dataset {delete_id}: {dataset_name}")
                    fo.delete_dataset(dataset_name)
            return

        if params.start_app == 2:
            app_config = fo.app_config.copy()
            app_config.show_confidence = False
            app_config.show_label = False
            app_config.show_tooltip = False
            app_config.show_index = False
            # print(app_config)

            dataset_names = get_datasets(params.filter, allow_empty=False)
            datasets_str = "\n".join(dataset_names)
            print(f"dataset_names:\n{datasets_str}")
            dataset = fo.load_dataset(dataset_names[0])
            app_params = dict(dataset=dataset, remote=params.remote, config=app_config)
            if params.address:
                app_params.update(dict(address=params.address))
            if params.port:
                app_params.update(dict(port=params.port))
            session = fo.launch_app(**app_params)
            wait_t = -1 if params.permanent else 0
            session.wait(wait_t)
            session.close()
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

    models_suffix = "_".join(params.model_suffixes)

    vis_dataset_name = f"{params.project_name}-{models_suffix}"
    if params.port:
        vis_dataset_name = f"{vis_dataset_name}-{params.port}"

    if params.filter.iall:
        include_suffix = "_".join(params.filter.iall)
        vis_dataset_name = f"{vis_dataset_name}-{include_suffix}"

    if params.chunk_id >= 0:
        vis_dataset_name = f"{vis_dataset_name}-chunk_{params.chunk_id}"

    if params.grouped:
        vis_dataset_name = f"{vis_dataset_name}-grouped"

    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    vis_dataset_name = f"{vis_dataset_name}-{timestamp}"

    print(f"\ncreating vis dataset: {vis_dataset_name}\n")

    with make_client(**client_cfg) as client:

        tasks_dict = [task.__dict__ for task in client.tasks.list()]
        projects_dict = [project.__dict__ for project in client.projects.list()]

        task_name_to_obj = {task["_model"]["name"]: task for task in tasks_dict}
        relevant_task_names = list(task_name_to_obj.keys())

        relevant_task_names = params.filter.apply(relevant_task_names)

        assert relevant_task_names, "no relevant tasks found"

        relevant_task_names.sort()

        task_name_to_obj = {
            task_name: task_name_to_obj[task_name] for task_name in relevant_task_names
        }
        task_name_to_id = {
            task_name: task_name_to_obj[task_name]["_model"]["id"]
            for task_name in relevant_task_names
        }

        project_name_to_id = {
            project["_model"]["name"]: project["_model"]["id"] for project in projects_dict
        }
        project_name_to_dict = {
            project["_model"]["name"]: project["_model"] for project in projects_dict
        }

        if params.local:
            vis_root_dir_path = linux_path(params.root_dir, params.vis_dir, vis_dataset_name)
            os.makedirs(vis_root_dir_path, exist_ok=True)
        else:
            try:
                dataset = fo.Dataset(vis_dataset_name, persistent=params.persistent)
            except ValueError as e:
                print(e)
                print("using auto-generated dataset name")
                dataset = fo.Dataset()

            app_config_ds = dataset.app_config
            app_config_ds.color_scheme = fo.ColorScheme(
                color_by="field",
                fields=[
                    {
                        "path": model_suffix,
                        "fieldColor": params.model_colors[model_id],
                    }
                    for model_id, model_suffix in enumerate(params.model_suffixes)
                ],
            )

            # app_config_global = fo.DatasetAppConfig
            # sidebar_groups = app_config_global.default_sidebar_groups(dataset)
            # active_fields = app_config_global.default_active_fields(dataset)

            if params.grouped:
                dataset.add_group_field("model")

        image_exts = ["jpg", "jpeg", "bmp", "png", "tif", "webp"]

        for subdir_id, subdir in enumerate(subdirs):

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
            for model_id, model_suffix in enumerate(params.model_suffixes):

                model_color_rgb = hex_to_rgb(params.model_colors[model_id])

                if params.local:
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

                project_id = project_name_to_id[project_name]
                project_dict = project_name_to_dict[project_name]
                task_name = f"{project_name}-{task_suffix}"
                if params.chunk_id >= 0:
                    task_name = f"{task_name}-{params.chunk_id}"

                if task_name not in task_name_to_id:
                    if params.ignore_invalid:
                        print(f"Skipping invalid task: {task_name}")
                        continue
                    else:
                        raise AssertionError(f"invalid task_name: {task_name}")

                task_obj = task_name_to_obj[task_name]
                task_id = task_name_to_id[task_name]
                task_dict = task_obj["_model"]
                task = client.tasks.retrieve(task_id)

                labels = task.get_labels()

                label_id_to_name = {label["id"]: label["name"] for label in labels}
                frames_info = task.get_frames_info()

                annotations = task.get_annotations()
                annotations_dict = annotations.to_dict()
                shapes = annotations["shapes"]

                n_model_objs_all = 0

                pbar = tqdm(
                    enumerate(frames_info),
                    total=len(frames_info),
                )

                for frame_id, frame_info in pbar:
                    frame_dict = frame_info.to_dict()
                    frame_w, frame_h = frame_dict["width"], frame_dict["height"]

                    frame_name = frame_dict["name"]
                    frame_path = linux_path(subdir, frame_name)
                    assert os.path.exists(frame_path), f"nonexistent frame_path: {frame_path}"

                    frame_shapes = [
                        shape.to_dict() for shape in shapes if shape["frame"] == frame_id
                    ]

                    # frame_points = [shape["points"] for shape in frame_shapes]
                    # frame_bbs = [points[-4:] for points in frame_points]
                    # frame_areas = [(bb[2] - bb[0]) * (bb[3] - bb[1]) for bb in frame_bbs]
                    # frame_points_len = [len(points) for points in frame_points]

                    if params.local:
                        frame_img = Image.open(frame_path)

                        frame_img_np = np.asarray(frame_img)
                        assert frame_img_np.shape[:2] == (frame_h, frame_w), "frame size mismatch"

                        # frame_mask = np.zeros((frame_h, frame_w), dtype=np.int32)
                        frame_mask = np.zeros_like(frame_img_np)
                    else:
                        if params.grouped:
                            try:
                                group = file_path_to_group[frame_path]
                            except KeyError:
                                file_path_to_group[frame_path] = group = fo.Group()
                            sample = fo.Sample(
                                filepath=frame_path, model=group.element(model_suffix)
                            )
                        else:
                            try:
                                sample = file_path_to_sample[frame_path]
                            except KeyError:
                                file_path_to_sample[frame_path] = sample = fo.Sample(
                                    filepath=frame_path
                                )
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
                                label=label,
                                bounding_box=[xmin, ymin, bb_w, bb_h],
                                mask=obj_mask_cropped,
                            )
                            detections.append(detection)

                    n_frame_objs = shape_id
                    # n_frame_objs = len(frame_shapes)
                    n_model_objs_all += n_frame_objs
                    pbar.set_description(f"{model_suffix} ({n_model_objs_all} objs): {task_name}")

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
                        if params.grouped:
                            sample["detections"] = fo.Detections(detections=detections)
                        else:
                            sample[model_suffix] = fo.Detections(detections=detections)

                        samples.append(sample)
                        # break

            if not params.local:
                dataset.add_samples(samples)
            # break

        if not params.local and params.start_app:
            app_params = dict(dataset=dataset, remote=params.remote)
            if params.port:
                app_params.update(dict(port=params.port))
            session = fo.launch_app(**app_params)

            session.wait(0)
            session.close()


if __name__ == "__main__":
    main()
