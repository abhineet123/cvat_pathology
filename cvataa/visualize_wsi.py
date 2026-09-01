import os
import numpy as np
from collections import defaultdict

# np.set_printoptions(legacy="1.25")

import cv2

import random
import openslide
import tifffile
import shapely
import paramparse
from datetime import datetime
from tqdm import tqdm
from PIL import Image
import compress_json

from stitch_tiles import collect_groups
import cell_seg_utils as utils


class GroupBy:
    none = 0
    model = 1
    label = 2


class ColorBy:
    model = 1
    label = 2
    model_and_label = 2


class Params(paramparse.CFG):
    """
    :ivar grp: how to group the fiftyone datasets
        grp=0: no grouping
        grp=1: group by model
        grp=2: group by class
    """

    def __init__(self):
        paramparse.CFG.__init__(self, cfg_prefix="vw")

        self.filter = utils.Filter()
        self.auth = utils.CVATAuth()

        self.cvat_mode = 0
        self.sort_by_id = 0

        self.models = []
        self.prefixes = []
        self.suffixes = []
        self.classifier_suffix = ""

        self.wsi_root_dir = "/data/PDL1-2026"
        self.wsi_dir = ""
        self.wsi_exts = [
            ".svs",
        ]
        self.mask_ext = ".tiff"
        self.ann_ext = ".geojson"

        self.tiles_root_dir = "/data/PDL1-2026-Tiles"
        self.tiles_dirs = []

        self.ann_dir_root = "/data/PDL1-2026-Detections"
        self.ann_dir = ""

        self.eval_dir_root = "lists/eval"
        self.eval_dir = ""
        self.eval_type = -1
        self.eval_start_id = 0
        self.eval_end_id = -1

        self.label_sets = []
        self.labels_to_ignore = ["roi", "tile"]
        self.map_labels = 0

        self.vis_name = ""
        self.vis_suffixes = []
        self.vis_model_suffix = ""
        self.shared_vis = ""

        self.recursive = 0

        self.delete_mode = 0
        self.config_db = ""

        self.grp = 1

        self.persistent = 1
        self.ignore_name_failure = 0

        self.address = ""
        self.permanent = 0
        self.port = 0
        self.remote = 0
        self.start_app = 0
        self.ignore_invalid = 0

        self.chunk_size = 100
        self.max_chunks = 0
        self.randomize_tiles = 0
        self.samples = 0

        self.time_suffix = 0
        self.load_existing = 0
        self.remove_existing = 1
        self.append_existing = 0

        self.excp_wait_t = 120
        self.verbose = 1

        self.opacity = 0.25
        self.vis = 0
        self.alpha = 0.25

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


def cf_color_by_model(models: list, cols):
    color_fields = [
        {
            "path": model_name,
            "fieldColor": cols[model_id],
        }
        for model_id, model_name in enumerate(models)
    ]
    return color_fields


def cf_color_by_label(labels: dict):
    color_fields = [
        {
            "path": label_name,
            "fieldColor": label_col,
        }
        for label_name, label_col in labels.items()
    ]
    return color_fields


def cf_color_by_model_and_label(models, classes, cols, shared_cols):
    color_fields = []

    col_id = 0
    for model in models:
        for class_name, class_col in classes.items():
            color_field = {
                "path": f"{model}-{class_name}",
                "fieldColor": class_col if shared_cols else cols[col_id],
            }
            color_fields.append(color_field)
    return color_fields


def cf_group_by_model(model_to_labels, cols):
    """one or more models, each with its own set of classes"""

    color_fields = []

    for model_id, (model, labels) in enumerate(model_to_labels.items()):
        n_labels = len(labels)
        model_col = cols[model_id]
        color_field = {
            "path": model,
            "fieldColor": model_col,
            "colorByAttribute": "label",
            "valueColors": [
                {"value": label_name, "color": model_col if n_labels == 1 else label_col}
                for label_name, label_col in labels.items()
            ],
        }
        color_fields.append(color_field)

    return color_fields


def cf_group_by_label(models, labels, cols):
    """one or more models, all with the same classes"""
    color_fields = []
    n_models = len(models)

    for label_name, label_col in labels.items():

        color_field = {
            "path": label_name,
            "fieldColor": label_col,
            "colorByAttribute": "label",
            "valueColors": [
                {
                    "value": model,
                    "color": label_col if n_models == 1 else cols[model_id],
                }
                for model_id, model in enumerate(models)
            ],
        }
        color_fields.append(color_field)

    return color_fields


def get_vis_color_fields(group_by, model_to_labels, models, label_sets, cols):
    n_models = len(models)
    n_label_sets = len(label_sets)

    if group_by == GroupBy.model:
        assert n_models > 1, "Grouping by models is not possible with a single model"
        color_fields = cf_group_by_model(model_to_labels, cols)
        """one color for each label"""
        color_by = ColorBy.label
    elif group_by == GroupBy.label:
        """one or more models, all models have the same classes - one group for each label showing nuclei of that type form all models"""
        assert n_label_sets == 1, "Grouping by labels is not supported with multiple class_sets"
        labels = utils.label_set_info[label_sets[0]]
        assert len(labels) > 1, "Grouping by labels is not possible with a single label"
        """one color for each model"""
        # raise NotImplementedError("grouping by labels is not implemented yet")
        color_fields = cf_group_by_label(models, labels, cols)
        color_by = ColorBy.model
    else:
        assert n_label_sets == 1, "multiple class_sets is not supported without grouping"

        labels = utils.label_set_info[label_sets[0]]
        n_labels = len(labels)

        if n_models == 1:
            """one color for each label"""
            color_fields = cf_color_by_label(labels)
            color_by = ColorBy.label
        else:
            if n_labels == 1:
                """one color for each model"""
                color_fields = cf_color_by_model(models, cols)
                color_by = ColorBy.model
            else:
                raise NotImplementedError(
                    "support for multiple models and multiple classes is not implemented yet"
                )
                """one color for each combination of model and class"""
                color_fields = cf_color_by_model_and_label(models, labels, cols, shared_cols=True)
                color_by = ColorBy.model_and_label

    return color_fields, color_by


def init_fo_dataset(params: Params, vis_dataset_name, color_fields):
    import fiftyone as fo
    from visualize_tasks import get_datasets

    vis_dataset_names = get_datasets(params.filter)
    dataset_loaded = False
    if vis_dataset_name in vis_dataset_names:
        if params.load_existing:
            print(f"loading existing dataset: {vis_dataset_name}\n")
            dataset = fo.load_dataset(vis_dataset_name)
            dataset_loaded = True
        elif params.remove_existing:
            print(f"deleting existing dataset: {vis_dataset_name}\n")
            fo.delete_dataset(vis_dataset_name)
        else:
            raise AssertionError(f"existing dataset found: {vis_dataset_name}")

    if dataset_loaded:
        return dataset_loaded, dataset

    print(f"\ncreating vis dataset: {vis_dataset_name}\n")
    try:
        dataset = fo.Dataset(vis_dataset_name, persistent=params.persistent)
    except ValueError as e:
        if params.ignore_name_failure:
            print(e)
            print("using auto-generated dataset name")
            dataset = fo.Dataset()
        else:
            raise e

    if params.grp == GroupBy.model:
        dataset.add_group_field("model")
    elif params.grp == GroupBy.label:
        dataset.add_group_field("cell_type")
        # raise NotImplementedError("grouping by labels is not implemented yet")

    app_config_ds = dataset.app_config

    if params.grp:
        app_config_ds.color_scheme = fo.ColorScheme(
            color_by="value",
            opacity=params.opacity,
            fields=color_fields,
        )
    else:
        app_config_ds.color_scheme = fo.ColorScheme(
            color_by="field",
            opacity=params.opacity,
            fields=color_fields,
        )
    return dataset_loaded, dataset


def detections_geojson_to_mask(
    ann_dir,
    model,
    wsi_file_name,
    mask_path,
    mask_h,
    mask_w,
    labels,
    labels_to_ignore,
):

    ann_dir_path = utils.linux_path(ann_dir, model, wsi_file_name)

    features = utils.load_geojson_as_chunks(ann_dir_path)

    panoptic_mask = np.zeros((mask_h, mask_w, 2), dtype=np.int32)
    label_names = list(labels.keys())

    # assert len(features) < len(all_rgb_cols), "too many cells for 8 bit RGB image"

    n_features = len(features)
    for feat_id, feat in tqdm(
        enumerate(features), desc="writing annotations to mask", total=n_features
    ):
        feat_properties = feat["properties"]
        if "classification" not in feat_properties:
            continue

        class_info = feat_properties["classification"]
        try:
            class_name = class_info["name"]
        except KeyError:
            class_names_ = class_info["names"]
            class_name = [cls for cls in class_names_ if cls in label_names]
            assert len(class_name) == 1, f"multiple matching classes found: {class_name}"
            class_name = class_name[0]

        # 0 is background
        col_id = feat_id + 1

        if class_name in labels_to_ignore:
            continue

        class_id = label_names.index(class_name) + 1

        geom = shapely.geometry.shape(feat["geometry"])
        if geom.geom_type == "MultiPolygon":
            for geom_ in geom.geoms:
                utils.draw_geom_to_mask(geom_, panoptic_mask, color=(col_id, class_id))
        else:
            utils.draw_geom_to_mask(geom, panoptic_mask, color=(col_id, class_id))

    panoptic_mask = panoptic_mask.transpose((2, 0, 1))
    print(f"saving mask to {mask_path}")
    tifffile.imwrite(
        mask_path,
        panoptic_mask,
        bigtiff=True,
        compression="zlib",
        photometric=None,
        metadata=None,
    )
    # return panoptic_mask


def vis_tile_mask(tile_path, tile_mask, inst_cols, class_cols, alpha):
    inst_mask, class_mask = tile_mask
    inst_mask_rgb = utils.instance_mask_to_rgb(inst_mask, inst_cols)
    cls_mask_rgb = utils.instance_mask_to_rgb(class_mask, class_cols)

    source_tile = np.array(Image.open(tile_path))

    inst_mask_overlaid = utils.overlay_cells(source_tile, inst_mask_rgb, alpha)
    cls_mask_overlaid = utils.overlay_cells(source_tile, cls_mask_rgb, alpha)

    source_tile = cv2.cvtColor(source_tile, cv2.COLOR_RGB2BGR)
    cv2.imshow("source_tile", source_tile)

    inst_mask_overlaid = cv2.cvtColor(inst_mask_overlaid, cv2.COLOR_RGB2BGR)
    cls_mask_overlaid = cv2.cvtColor(cls_mask_overlaid, cv2.COLOR_RGB2BGR)
    cv2.imshow("inst_mask_overlaid", inst_mask_overlaid)
    cv2.imshow("cls_mask_overlaid", cls_mask_overlaid)

    inst_mask_rgb = cv2.cvtColor(inst_mask_rgb, cv2.COLOR_RGB2BGR)
    cls_mask_rgb = cv2.cvtColor(cls_mask_rgb, cv2.COLOR_RGB2BGR)
    cv2.imshow("inst_mask", inst_mask_rgb)
    cv2.imshow("cls_mask", cls_mask_rgb)

    k = cv2.waitKey(0)
    if k == 27:
        exit(0)


def create_cvat_project_lla(client, project_name, label_names, label_cols):
    from cvat_sdk.api_client import exceptions

    print("getting cvat projects list with low level api...")
    project_name_to_id = utils.get_cvat_projects_lla(client)

    if project_name in project_name_to_id:
        print(f"deleting existing project: {project_name}")
        project_id = project_name_to_id[project_name]
        try:
            client.projects_api.destroy(
                project_id,
            )
        except exceptions.ApiException as e:
            raise AssertionError(f"Failed to delete project:\n{e}")

    print(f"creating project: {project_name}")

    project_dict = utils.create_project_lla(
        client=client,
        cfg_dict=None,
        name=project_name,
        label_names=label_names,
        label_cols=label_cols,
    )

    project_id = project_dict["id"]

    project_name_to_id = utils.get_cvat_projects_lla(client)

    assert project_id == project_name_to_id[project_name]

    project_id = project_name_to_id[project_name]
    return project_id


def upload_cvat_images_and_annotations(client, task, image_paths, frame_name_to_shapes):
    n_images = len(image_paths)

    assert len(frame_name_to_shapes) == n_images, "frame_name_to_shapes length mismatch"

    print(f"uploading {n_images} images to cvat...")
    utils.upload_images_hla(client, task, image_paths)

    from cvat_sdk.datasets.task_dataset import TaskDataset
    from cvat_sdk.auto_annotation.driver import _AnnotationMapper
    import cvat_sdk.models as models

    dataset = TaskDataset(client, task.id, load_annotations=False)

    assert len(dataset.samples) == n_images, "dataset length mismatch"

    labels = dataset.labels
    # labels = tuple(task.get_labels())

    mapper = _AnnotationMapper(
        client.logger,
        labels,
        labels,
        allow_unmatched_labels=False,
        conv_mask_to_poly=False,
    )
    tags = []
    shapes = []
    for sample_id, sample in tqdm(
        enumerate(dataset.samples), desc="remapping cvat shapes", total=n_images
    ):
        frame_shapes = frame_name_to_shapes[sample.frame_name]
        frame_tags, frame_shapes = mapper.validate_and_remap(frame_shapes, sample.frame_index)
        shapes.extend(frame_shapes)
        tags.extend(frame_tags)

    print(f"uploading {len(shapes)} shapes to cvat...")
    client.tasks.api.partial_update_annotations(
        "create",
        task.id,
        patched_labeled_data_request=models.PatchedLabeledDataRequest(
            tags=tags,
            shapes=shapes,
        ),
    )


def main():
    params: Params = paramparse.process(Params)

    assert params.models, "models must be provided"

    models = params.models
    suffixes = params.suffixes
    label_sets = params.label_sets
    model_to_suffix = None

    if suffixes:
        assert len(models) == 1, "model suffixes are only supported with one model"

        if params.classifier_suffix:
            suffixes = [f"{suffix}-{params.classifier_suffix}" for suffix in suffixes]

        models = [f"{models[0]}-{suffix}" for suffix in suffixes]
        model_to_suffix = {model: suffix for model, suffix in zip(models, suffixes, strict=True)}

        if not label_sets:
            label_sets = suffixes[:]

    assert label_sets, "label_sets must be provided"

    n_label_sets = len(label_sets)
    n_models = len(models)

    if params.cvat_mode:
        # assert n_models == 1, "only single model is currently supported in cvat_mode"
        assert n_label_sets == 1, "only single label_set is currently supported in cvat_mode"

    if n_label_sets == 1:
        model_to_label_set = {model: label_sets[0] for model in models}
        shared_labels = utils.label_set_info[label_sets[0]]
    else:
        assert n_label_sets == n_models, f"mismatch between n_label_sets and n_models"
        model_to_label_set = {
            model: label_set for label_set, model in zip(label_sets, models, strict=True)
        }
        shared_labels = None

    model_to_labels = {
        model: utils.label_set_info[label_set] for model, label_set in model_to_label_set.items()
    }
    if params.map_labels:
        assert model_to_suffix is not None, "suffixes must be provided to map labels"
        model_to_label_maps = {
            model: utils.label_map_info[label_set]
            for model, label_set in model_to_label_set.items()
        }

    vis_cp, vis_models = utils.remove_common_prefix(models)
    vis_cs, vis_models = utils.remove_common_suffix(vis_models)

    vis_model_to_labels = {
        vis_model: model_to_labels[model]
        for vis_model, model in zip(vis_models, models, strict=True)
    }

    wsi_files = utils.get_wsi_files(
        params.wsi_root_dir,
        params.wsi_dir,
        params.wsi_exts,
        params.recursive,
        params.filter,
        params.sort_by_id,
    )
    tiles_dirs = utils.get_tiles_dirs(
        params.tiles_root_dir, params.tiles_dirs, params.recursive, params.filter, params.sort_by_id
    )

    n_wsi_files, wsi_file_names = utils.check_wsi_files_and_slides(wsi_files, tiles_dirs)

    # print(f"Found {n_wsi_files} matching WSI(s):\n{utils.to_str_multi([wsi_files, tiles_dirs])}\n")

    if params.eval_dir:
        eval_name = "pass" if params.eval_type == 1 else "fail" if params.eval_type == 0 else "all"
        eval_dir_path = utils.linux_path(params.eval_dir_root, params.eval_dir)

        """TODO: integrate eval excel to json conversion"""
        # if not os.path.isdir(eval_dir_path):
        #     eval_excel_path = eval_dir_path + ".xlsx"
        #     if os.path.isfile(eval_excel_path):
        #         eval_excel_to_json(eval_excel_path)
        #     else:
        #         raise AssertionError(f"invalid eval_dir: {params.eval_dir}")

        eval_path = utils.linux_path(eval_dir_path, f"{eval_name}.json.gz")
        print(f"loading eval samples from: {eval_path}")
        wsi_to_tile_names = compress_json.load(eval_path)
        wsi_name_to_path = {
            wsi_file_name: wsi_file
            for wsi_file, wsi_file_name in zip(wsi_files, wsi_file_names, strict=True)
        }
        wsi_to_tiles = {
            wsi_name_to_path[wsi_name]: collect_groups(tiles, enforce_unity=True)
            for wsi_name, tiles in wsi_to_tile_names.items()
        }
        wsi_to_tiles, eval_ids_suffix = params.filter.apply_ids(
            list(wsi_to_tiles.items()), ids=(params.eval_start_id, params.eval_end_id), suffix=True
        )
        wsi_to_tiles = dict(wsi_to_tiles)
        n_wsi_files = len(wsi_to_tiles)

        eval_prefix = utils.path_to_name(params.eval_dir) + "-" + eval_name
        if eval_ids_suffix:
            eval_prefix = f"{eval_prefix}-{eval_ids_suffix}"

    else:
        wsi_to_tiles = {
            wsi_file: collect_groups(tiles_dir, enforce_unity=True)
            for wsi_file, tiles_dir in zip(wsi_files, tiles_dirs, strict=True)
        }
        eval_prefix = ""

    wsi_names = [utils.path_to_name(wsi_file) for wsi_file in wsi_to_tiles.keys()]
    print(f"running on {n_wsi_files} WSIs:\n{utils.to_str(wsi_names)}\n")

    if not params.cvat_mode:
        import fiftyone as fo

        color_fields, color_by = get_vis_color_fields(
            params.grp, vis_model_to_labels, vis_models, label_sets, params.cols
        )

    ann_dir = params.ann_dir

    if not ann_dir:
        ann_dir = params.wsi_dir

    if params.ann_dir_root:
        ann_dir = utils.linux_path(params.ann_dir_root, ann_dir)

    vis_name = params.vis_name
    if not vis_name:
        vis_model_suffix = params.vis_model_suffix
        if not vis_model_suffix:
            vis_model_suffix = "_".join(vis_models)
            if vis_cp:
                vis_model_suffix = f"{vis_cp}{vis_model_suffix}"
            if vis_cs:
                vis_model_suffix = f"{vis_model_suffix}{vis_cs}"

        vis_name = f"{vis_model_suffix}"

        if label_sets != suffixes:
            label_suffix = "_".join(label_sets)
            vis_name = f"{vis_name}-{label_suffix}"

        # if params.filter.iall:
        #     include_suffix = "_".join(params.filter.iall)
        #     vis_dataset_name = f"{vis_dataset_name}-{include_suffix}"

        if eval_prefix:
            vis_name = f"{eval_prefix}-{vis_name}"

        if params.randomize_tiles:
            vis_name = f"{vis_name}-rnd"

        if params.vis_suffixes:
            vis_suffix = "-".join(params.vis_suffixes)
            vis_name = f"{vis_name}-{vis_suffix}"

        if params.grp == GroupBy.model:
            vis_name = f"{vis_name}-grp_model"
        elif params.grp == GroupBy.label:
            vis_name = f"{vis_name}-grp_label"
        else:
            if color_by == ColorBy.model:
                vis_name = f"{vis_name}-col_model"
            elif color_by == ColorBy.label:
                vis_name = f"{vis_name}-col_label"

        if params.time_suffix:
            timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
            vis_name = f"{vis_name}-{timestamp}"

    shared_dataset_name = f"wsi-{vis_name}"

    if params.cvat_mode:
        from cvat_sdk import make_client

        # import cvat_sdk.api_client as api_client

        cvat_cfg_dict = params.auth.to_cfg()

        # cvat_cfg = api_client.Configuration(**cvat_cfg_dict)

        cvat_client_hla = make_client(**cvat_cfg_dict)
        cvat_client_lla = cvat_client_hla.api_client

        if n_models > 1 and label_sets[0] == "seg_only":
            """seg only with multiple models"""
            cvat_labels = {
                model: params.cols[model_id] for model_id, model in enumerate(vis_models)
            }
            cvat_model_as_label = True
        else:
            cvat_labels = shared_labels
            cvat_model_as_label = False

        cvat_project_id = create_cvat_project_lla(
            cvat_client_lla,
            project_name=shared_dataset_name,
            label_names=list(cvat_labels.keys()),
            label_cols=list(cvat_labels.values()),
        )
        cvat_task_name_to_id = utils.get_cvat_tasks_lla(cvat_client_lla)
        if params.shared_vis:
            cvat_task = utils.create_empty_cvat_task(
                cvat_client_hla, cvat_project_id, shared_dataset_name, cvat_task_name_to_id
            )
            cvat_image_paths = []
            tile_name_to_cvat_shapes = defaultdict(list)
    else:
        if params.shared_vis:
            _, wsi_dataset = init_fo_dataset(params, shared_dataset_name, color_fields)

    for wsi_file_id, (
        wsi_file,
        tiles_all,
    ) in enumerate(wsi_to_tiles.items()):
        wsi_file_name = utils.path_to_name(wsi_file)

        if not params.shared_vis:
            wsi_dataset_name = f"wsi-{params.wsi_dir}-{wsi_file_name}-{vis_name}"
            if params.cvat_mode:
                cvat_task = utils.create_empty_cvat_task(
                    cvat_client_hla, cvat_project_id, wsi_dataset_name, cvat_task_name_to_id
                )
                cvat_image_paths = []
                tile_name_to_cvat_shapes = defaultdict(list)
            else:
                _, wsi_dataset = init_fo_dataset(params, wsi_dataset_name, color_fields)

        wsi = openslide.OpenSlide(wsi_file)
        wsi_w, wsi_h = wsi.dimensions

        # print(f"\nwsi {wsi_file_id+1} / {n_wsi_files}: {wsi_file_name}")

        if params.randomize_tiles:
            random.shuffle(tiles_all)

        if len(tiles_all) > params.samples > 0:
            tiles_all = tiles_all[: params.samples]

        if len(tiles_all) > params.chunk_size > 0:
            if params.randomize_tiles and params.samples > 0:
                """
                assume that randomization was done for the purpose of sampling and re-sort tiles before chunking to keep the tiles in each chunk as spatially contiguous as possible and therefore keep the size of each WSI chunk ROI as small as possible
                """
                if params.sort_by_id:
                    tiles_all.sort(key=lambda x: utils.path_to_id(x["path"]))
                else:
                    tiles_all.sort(key=lambda x: utils.path_to_name(x["path"]))
            tiles_chunks = list(utils.chunks(tiles_all, params.chunk_size))
        else:
            tiles_chunks = [
                tiles_all,
            ]

        n_chunks = len(tiles_chunks)

        if n_chunks > params.max_chunks > 0:
            tiles_chunks = tiles_chunks[: params.max_chunks]
            n_chunks = params.max_chunks

        wsi_msg = f"wsi {wsi_file_id+1}/{n_wsi_files}: {wsi_file_name}"

        for chunk_id, tiles_chunk in enumerate(tiles_chunks):

            if params.cvat_mode:
                tile_paths = [tile["path"] for tile in tiles_chunk]
                cvat_image_paths += tile_paths
            else:
                all_chunk_samples = []
                tile_path_to_group = dict() if params.grp else None
                tile_path_to_sample = dict() if params.grp == GroupBy.none else None
                label_to_samples = defaultdict(dict) if params.grp == GroupBy.label else None
                label_to_detections = (
                    defaultdict(lambda: defaultdict(list))
                    if params.grp == GroupBy.label
                    or (params.grp == GroupBy.none and color_by == ColorBy.label)
                    else None
                )

            n_models = len(models)

            min_xs, min_ys = zip(*[(tile_info["x"], tile_info["y"]) for tile_info in tiles_chunk])
            max_xs, max_ys = zip(
                *[
                    (tile_info["x"] + tile_info["w_meta"], tile_info["y"] + tile_info["h_meta"])
                    for tile_info in tiles_chunk
                ]
            )

            roi_min_x, roi_min_y = np.amin(min_xs), np.amin(min_ys)
            roi_max_x, roi_max_y = np.amax(max_xs), np.amax(max_ys)
            roi_w, roi_h = roi_max_x - roi_min_x, roi_max_y - roi_min_y

            # print(f"Chunk ROI dimensions: {roi_w} x {roi_h}")
            chunk_msg = (
                f"chunk {chunk_id+1}/{n_chunks}: ({roi_min_x}, {roi_min_y}) {roi_w} x {roi_h} "
            )

            for model_id, (model, vis_model) in enumerate(zip(models, vis_models, strict=True)):
                model_msg = f"model {model_id+1}/{n_models}: {model}"
                print(f"\n{wsi_msg} {chunk_msg} {model_msg}")

                labels = model_to_labels[model]
                label_cols = list(labels.values())
                label_names = list(labels.keys())

                n_labels = len(labels)

                if params.map_labels:
                    suffix = model_to_suffix[model]
                    label_map = model_to_label_maps[model][suffix]
                    label_names_to_map = list(label_map.keys())

                wsi_mask_path = utils.linux_path(
                    ann_dir, model, f"{wsi_file_name}", f"{wsi_file_name}.tiff"
                )

                if chunk_id == 0:
                    # double check that dict ordering is enforced
                    assert all(
                        labels[label_name] == label_col
                        for label_name, label_col in zip(label_names, label_cols, strict=True)
                    )

                    if not os.path.exists(wsi_mask_path):
                        detections_geojson_to_mask(
                            ann_dir,
                            model,
                            wsi_file_name,
                            wsi_mask_path,
                            wsi_h,
                            wsi_w,
                            labels,
                            params.labels_to_ignore,
                        )
                    print(f"reading wsi mask from {wsi_mask_path}")

                chunk_mask = tifffile.imread(
                    wsi_mask_path, selection=np.s_[0:2, roi_min_y:roi_max_y, roi_min_x:roi_max_x]
                )
                n_tiles = len(tiles_chunk)

                for tile in tqdm(tiles_chunk, desc=f"processing tiles", total=n_tiles):

                    x1, y1, tile_w, tile_h = tile["x"], tile["y"], tile["w_meta"], tile["h_meta"]
                    x2, y2 = x1 + tile_w, y1 + tile_h

                    x1, y1, x2, y2 = utils.add_offset([x1, y1, x2, y2], [-roi_min_x, -roi_min_y])

                    tile_path = tile["path"]
                    tile_file_name = os.path.basename(tile_path)

                    tile_mask = chunk_mask[:, y1:y2, x1:x2]
                    # tile_mask = tifffile.imread(wsi_mask_path, selection=np.s_[0:2, y1:y2, x1:x2])

                    if params.vis:
                        vis_tile_mask(tile_path, tile_mask, params.cols, label_cols, params.alpha)

                    inst_mask, cls_mask = tile_mask
                    cell_ids = utils.instance_mask_to_ids(inst_mask)

                    if params.cvat_mode:
                        cvat_label_dicts = [label.to_dict() for label in cvat_task.get_labels()]
                        cvat_label_id_to_dict = {label["id"]: label for label in cvat_label_dicts}
                        cvat_label_name_to_id = {
                            label["name"]: label["id"] for label in cvat_label_dicts
                        }
                        cvat_results = []
                    else:
                        if params.grp:
                            try:
                                group = tile_path_to_group[tile_path]
                            except KeyError:
                                group = tile_path_to_group[tile_path] = fo.Group()

                            if params.grp == GroupBy.model:
                                """each tile has one sample for each model"""
                                sample = fo.Sample(
                                    filepath=tile_path, model=group.element(vis_model)
                                )
                                all_chunk_samples.append(sample)
                            elif params.grp == GroupBy.label:
                                """each tile has one sample for each label"""
                                sample = None
                                label_to_tile_samples = label_to_samples[tile_path]
                        else:
                            """each tile has only one sample"""
                            try:
                                sample = tile_path_to_sample[tile_path]
                            except KeyError:
                                sample = tile_path_to_sample[tile_path] = fo.Sample(
                                    filepath=tile_path
                                )
                                all_chunk_samples.append(sample)

                        if label_to_detections is not None:
                            label_to_tile_detections = label_to_detections[tile_path]

                        tile_detections = []

                    for i, cell_id in enumerate(cell_ids):
                        cell_inst_mask = inst_mask == cell_id
                        ys, xs = np.nonzero(cell_inst_mask)
                        xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
                        bb_w, bb_h = xmax - xmin, ymax - ymin

                        if bb_w < 2 or bb_h < 2:
                            continue

                        cell_inst_mask_cropped = cell_inst_mask[ymin : ymax + 1, xmin : xmax + 1]

                        bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

                        label_id = utils.class_mask_to_id(cls_mask, cell_inst_mask_cropped, bbox)
                        """class_id has an ofset of 1 to account for the background"""

                        if params.map_labels:
                            label_name = label_names_to_map[label_id - 1]
                            label_name = label_map[label_name]
                        else:
                            label_name = label_names[label_id - 1]

                        if params.cvat_mode:
                            from cvat_sdk import masks, auto_annotation

                            cvat_bbox = [float(xmin), float(ymin), float(xmax), float(ymax)]
                            cvat_points = masks.encode_mask(cell_inst_mask, cvat_bbox)
                            cvat_label_name = vis_model if cvat_model_as_label else label_name
                            cvat_label_id = cvat_label_name_to_id[cvat_label_name]
                            cvat_label_dict = cvat_label_id_to_dict[cvat_label_id]
                            cvat_attribute_name_to_id = {
                                attribute["name"]: attribute["id"]
                                for attribute in cvat_label_dict["attributes"]
                            }
                            result_dict = dict(
                                label_id=cvat_label_id,
                                points=cvat_points,
                                attributes=[
                                    dict(
                                        value=f"{model}",
                                        spec_id=cvat_attribute_name_to_id["model"],
                                    ),
                                ],
                            )
                            cvat_result = auto_annotation.mask(**result_dict)
                            cvat_results.append(cvat_result)
                        else:

                            xmin, ymin, xmax, ymax = (
                                float(xmin) / tile_w,
                                float(ymin) / tile_h,
                                float(xmax) / tile_w,
                                float(ymax) / tile_h,
                            )
                            bb_w, bb_h = xmax - xmin, ymax - ymin

                            detection = fo.Detection(
                                label=vis_model if color_by == ColorBy.model else label_name,
                                bounding_box=[xmin, ymin, bb_w, bb_h],
                                mask=cell_inst_mask_cropped,
                            )

                            if params.grp == GroupBy.label:
                                """create a new sample for each tile every time a new label is encountered for the first time"""
                                try:
                                    sample = label_to_tile_samples[label_name]
                                except KeyError:
                                    sample = label_to_tile_samples[label_name] = fo.Sample(
                                        filepath=tile_path, cell_type=group.element(label_name)
                                    )
                                    all_chunk_samples.append(sample)

                            """models are in the outer loop so all detections for each model for this tile can be collected directly but collecting all the detections for each label for this tile requires iterating over all the models"""
                            if label_to_detections is not None:
                                label_to_tile_detections[label_name].append(detection)
                            else:
                                tile_detections.append(detection)

                    if params.cvat_mode:
                        tile_name_to_cvat_shapes[tile_file_name] += cvat_results
                    else:
                        if params.grp == GroupBy.label:
                            """
                            we need all detctions in this tile for each label across all models
                            this can only be done after going through all of the models in the outer loop
                            """
                            pass
                        elif params.grp == GroupBy.model or color_by == ColorBy.model:
                            """all detctions in this tile for this model"""
                            sample[vis_model] = fo.Detections(detections=tile_detections)

                del chunk_mask

            if not params.cvat_mode:
                if label_to_detections is not None:
                    for tile_path, label_to_tile_detections in label_to_detections.items():
                        if label_to_samples is not None:
                            assert (
                                params.grp == GroupBy.label
                            ), "label_to_samples should only exist when grouping by label"

                            label_to_tile_samples = label_to_samples[tile_path]
                            for label_name in shared_labels.keys():
                                try:
                                    sample = label_to_tile_samples[label_name]
                                except:
                                    """none of the models have any detections of this type in this tile
                                    so create an empty sample"""
                                    group = tile_path_to_group[tile_path]
                                    sample = fo.Sample(
                                        filepath=tile_path, cell_type=group.element(label_name)
                                    )
                                    all_chunk_samples.append(sample)
                                try:
                                    tile_detections = label_to_tile_detections[label_name]
                                except:
                                    tile_detections = []
                                sample[label_name] = fo.Detections(detections=tile_detections)
                        else:
                            assert (
                                params.grp == GroupBy.none
                            ), "tile_path_to_sample should only exist when grouping is disabled"
                            sample = tile_path_to_sample[tile_path]
                            for label_name, tile_detections in label_to_tile_detections.items():
                                sample[label_name] = fo.Detections(detections=tile_detections)
                wsi_dataset.add_samples(all_chunk_samples)

        if not params.shared_vis and params.cvat_mode:
            upload_cvat_images_and_annotations(
                cvat_client_hla, cvat_task, cvat_image_paths, tile_name_to_cvat_shapes
            )

    if params.cvat_mode:
        if params.shared_vis:
            upload_cvat_images_and_annotations(
                cvat_client_hla, cvat_task, cvat_image_paths, tile_name_to_cvat_shapes
            )
        cvat_client_hla.close()


if __name__ == "__main__":
    main()
