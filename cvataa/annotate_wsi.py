import os
import sys

cvat_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(cvat_path)

import time
import json
import numpy as np
from pathlib import Path
from datetime import datetime

# np.set_printoptions(legacy="1.25")

import openslide
import tifffile
import copy
import subprocess

import cv2
import shapely


from tqdm import tqdm
import orjson
import gzip

import paramparse

from stitch_tiles import collect_groups

from cell_seg_wsi import CellSegWSIBase

from cell_seg_params import CellposeParams, CellVITParams, StarDistParams
from classifiers.cell_cls_params import QuPathMLPParams

from create_tissue_mask import load_annotations, burn_polygons_tiled

import cell_seg_utils as utils


class Params(paramparse.CFG):
    class Tile:
        """
        settings for tiling the WSI; only used when file_mode is disabled

        :ivar sz: tile size in pixels
        :ivar ovl: Overlap in pixels between consecutive tiles
        :ivar max: maximum number of tiles to process;
            ignored if <= 0;
            can be useful to speedup debugging
        :ivar vis: visualize tile locations including pairs of overlapping tiles
        """

        sz = 0
        ovl = 0
        max = 0
        vis = 0

    def __init__(self, cfg_prefix="aw"):
        paramparse.CFG.__init__(self, cfg_prefix=cfg_prefix)

        self.filter = utils.Filter()

        self.models = []

        self.cls = ""
        self.skip_seg = 0

        self.wsi_root_dir = ""
        self.wsi_dir = ""
        self.wsi_exts = [
            ".svs",
        ]
        self.mask_dir = "masks"
        self.mask_ext = ".tiff"

        self.ann_dir = "annotations"
        self.ann_ext = ".geojson.gz"

        self.tiles_root_dir = ""
        self.tiles_dirs = []

        self.output_root_dir = ""
        self.compression = "zlib"

        self.seg_output_path = ""
        self.cls_output_path = ""

        self.qp_export = 0
        self.qp_proj_path = ""
        self.qp_exe = "QuPath"
        self.qp_dir = "qupath"
        self.qp_export_script = "export_annotations_headless.groovy"

        self.file_mode = 0
        self.tissue_filter = 1
        self.recursive = 0
        self.nms_thresh = 0.5
        self.min_area = 5

        self.load_from_cache = 0
        self.save_to_cache = 1

        self.start_id = 0
        self.end_id = -1

        self.vis = 0

        self.roi_obj = 0
        self.tile_objs = 0

        self.cvit = CellVITParams()
        self.clps = CellposeParams()
        self.strd = StarDistParams()

        self.qmlp = QuPathMLPParams()

        self.tile = Params.Tile()
        # self.deploy = Params.Deploy()


def get_cls_model(model_name, params: Params):
    if not model_name:
        return None

    if model_name in ["qupath_mlp", "qp_mlp", "qp", "qmlp"]:
        from classifiers.qupath_mlp import QuPathMLP

        model = QuPathMLP(params=params.qmlp)
    else:
        raise AssertionError(f"invalid cls model {model_name}")

    return model


def get_seg_model(model_name, params: Params) -> CellSegWSIBase:
    if model_name in ["cellvit", "cvit"]:
        from cellvit_wsi import CellVITWSI

        model = CellVITWSI(params=params.cvit, file_mode=params.file_mode)
    elif model_name in ["cellpose", "clps"]:
        from cellpose_wsi import CellposeWSI

        model = CellposeWSI(params=params.clps, file_mode=params.file_mode)
    elif model_name in ["stardist", "strd"]:
        from stardist_wsi import StardistWSI

        model = StardistWSI(params=params.strd, file_mode=params.file_mode)
    else:
        raise AssertionError(f"invalid seg model {model_name}")

    return model


def segment_wsi(
    params: Params,
    seg_model,
    wsi_file,
    tiles_dir,
    tissue_mask_file,
    tissue_annotation_file,
    out_path,
    cache_path,
    label_map,
):
    print(f"Writing outputs to: {out_path}")
    os.makedirs(out_path, exist_ok=True)

    if params.file_mode:
        """
        pass the WSI file itself to the seg model and let it process the file (e.g. tiling/untiling/nms etc) as it wishes
        e.g. cellvit comes bundled with a pretty-sophisticated WSI processing pipeline
        """
        seg_model.detect_in_file(wsi_file, tissue_mask_file, tissue_annotation_file, out_path)
        return

    wsi_name = utils.path_to_name(wsi_file, remove_ext=True)

    wsi_tissue_mask = tifffile.imread(tissue_mask_file)
    # wsi_tissue_mask = openslide.OpenSlide(tissue_mask_file)

    wsi = openslide.OpenSlide(wsi_file)
    wsi_w, wsi_h = wsi.dimensions
    print(f"WSI dimensions: {wsi_w} x {wsi_h}")

    if tiles_dir:
        groups = collect_groups(tiles_dir)
        if not groups:
            raise FileNotFoundError(
                f"No tile files matching the expected QuPath pattern were found in: {params.tile_dir}"
            )

        assert len(groups) == 1, "multiple prefix groups found"

        tiles_info = next(iter(groups.values()), None)

        xs, ys = zip(*[(tile_info["x"], tile_info["y"]) for tile_info in tiles_info])
        roi_min_x, roi_max_x = np.amin(xs), np.amax(xs)
        roi_min_y, roi_max_y = np.amin(ys), np.amax(ys)
    else:
        polygons, bboxes = utils.load_annotations_from_qupath_geojson(
            tissue_annotation_file, verbose=params.verbose
        )
        bboxes = np.stack(bboxes, axis=0)

        min_xs, min_ys, max_xs, max_ys = bboxes[:, 0], bboxes[:, 1], bboxes[:, 2], bboxes[:, 3]

        roi_min_x, roi_max_x = np.amin(min_xs), np.amax(max_xs)
        roi_min_y, roi_max_y = np.amin(min_ys), np.amax(max_ys)

    roi_min_x, roi_min_y, roi_max_x, roi_max_y = [
        int(k) for k in [roi_min_x, roi_min_y, roi_max_x, roi_max_y]
    ]
    roi_bbox = [roi_min_x, roi_min_y, roi_max_x, roi_max_y]
    roi_w, roi_h = roi_max_x - roi_min_x, roi_max_y - roi_min_y

    print(f"ROI dimensions: {roi_w} x {roi_h}")

    # min_x, min_y = tiles_info[0]["x"], tiles_info[0]["y"]
    # roi_w, roi_h = tiles_info[0]["w_meta"], tiles_info[0]["h_meta"]

    # for tile_info in tiles_info:

    #     min_x, min_y = tile_info["x"], tile_info["y"]
    #     roi_w, roi_h = tile_info["w_meta"], tile_info["h_meta"]

    roi_tissue_mask = wsi_tissue_mask[roi_min_y:roi_max_y, roi_min_x:roi_max_x].astype(bool)

    all_cells = None

    if params.roi_obj:
        print(f"writing ROI object: {roi_bbox}")
        roi_label_id = utils.get_id_from_name(label_map, "roi")
        all_cells.append(
            {
                "type": roi_label_id,
                "id": f"roi",
                "mask": roi_tissue_mask,
                "wsi_bbox": roi_bbox,
                "area": int(roi_h * roi_w),
                "to_delete": 0,
                "ioa": {},
            }
        )

    if not params.tile.sz:
        """non-tiling mode"""
        """running big models like cellpose on the entire WSI at once can easily lead to out-of-memory issues"""
        print(f"extracting wsi ROI of size {roi_w} x {roi_h} and origin: [{min_x}, {min_y}]...")
        wsi_roi_pil = wsi.read_region(location=(min_x, min_y), level=0, size=(roi_w, roi_h))

        print(f"converting wsi ROI to numpy")
        wsi_roi = np.array(wsi_roi_pil)[..., :3]

        del wsi_roi_pil

        start_t = time.time()
        roi_cells = seg_model.detect(wsi_roi, (roi_min_x, roi_min_y))
        end_t = time.time()

        all_cells = roi_cells

        detection_t = end_t - start_t
        detection_fps = float(len(tiles_info)) / detection_t

        print(f"detection time: {detection_t} ({detection_fps:.2f} fps)")

    if params.load_from_cache:

        assert os.path.isdir(cache_path), f"nonexistent cache_path: {cache_path}"

        print(f"loading cache from {cache_path}")
        compression_kwarg = {}
        with gzip.open(
            utils.linux_path(cache_path, "tile_id_to_cells.json.gz"),
            mode="rb",
            **compression_kwarg,
        ) as fid:
            tile_id_to_cells = orjson.loads(
                fid.read(),
            )
        all_cells = [x for xs in tile_id_to_cells.values() for x in xs]

    if all_cells is not None:
        features = utils.save_cells_as_qupath_geojson(
            all_cells,
            out_path,
            label_map,
            min_area=params.min_area,
            chunk_size=0,
            output_wsi_name=wsi_name,
        )
        return features

    tile_id_to_roi_bbox, overlapping_tiles = utils.make_tiles(
        (roi_h, roi_w),
        tile_size=params.tile.sz,
        tile_overlap=params.tile.ovl,
        max_tiles=params.tile.max,
        vis=params.tile.vis,
    )

    if params.tissue_filter:
        valid_tile_ids = []
        for tile_id, tile_bbox_roi in tqdm(
            tile_id_to_roi_bbox.items(),
            desc="filtering tiles by tissue mask",
        ):
            min_x, min_y, max_x, max_y = utils.add_offset(tile_bbox_roi, (roi_min_x, roi_min_y))
            tile_tissue_mask = wsi_tissue_mask[min_y:max_y, min_x:max_x].astype(bool)

            if np.any(tile_tissue_mask):
                valid_tile_ids.append(tile_id)

        print(
            f"\nfound {len(valid_tile_ids)} / {len(tile_id_to_roi_bbox)} tiles to contain tissue\n"
        )
        tile_id_to_roi_bbox = {
            tile_id: tile_id_to_roi_bbox[tile_id] for i, tile_id in enumerate(valid_tile_ids)
        }
        overlapping_tiles = [
            tile_pair
            for tile_pair in overlapping_tiles
            if tile_pair[0] in valid_tile_ids and tile_pair[1] in valid_tile_ids
        ]

    # convert tile ROIs from tissue ROI space to WSI space
    tile_id_to_wsi_bbox = {
        tile_id: utils.add_offset(tile_bbox_roi, (roi_min_x, roi_min_y))
        for tile_id, tile_bbox_roi in tile_id_to_roi_bbox.items()
    }
    n_tiles = len(tile_id_to_roi_bbox)
    all_cells = []
    tile_id_to_cells = {}
    for tile_id, tile_bbox_roi in tqdm(
        tile_id_to_roi_bbox.items(),
        desc="runing inference on tiles",
        total=n_tiles,
    ):
        tile_bbox_wsi = tile_id_to_wsi_bbox[tile_id]
        min_x, min_y, max_x, max_y = tile_bbox_wsi
        tile_w, tile_h = max_x - min_x, max_y - min_y

        # if roi is smaller than the required tile size in either dimension, that size will be reduced to match the roi
        assert max_x == roi_max_x or tile_w == params.tile.sz, "tile width mismatch"
        assert max_y == roi_max_y or tile_h == params.tile.sz, "tile height mismatch"

        tile_tissue_mask = wsi_tissue_mask[min_y:max_y, min_x:max_x].astype(bool)

        if params.tile_objs:
            print(f"\nwriting tile object: {tile_bbox_wsi}\n")

            tile_label_id = utils.get_id_from_name(label_map, "tile")
            all_cells.append(
                {
                    "type": tile_label_id,
                    "id": f"tile-{tile_id}",
                    "mask": tile_tissue_mask,
                    "wsi_bbox": tile_bbox_wsi,
                    "area": int(tile_h * tile_w),
                    "to_delete": 0,
                    "ioa": {},
                }
            )
            if params.tile_objs == 2:
                """for debugging"""
                continue

        tile_img_pil = wsi.read_region(location=(min_x, min_y), level=0, size=(tile_w, tile_h))

        tile_img_np = np.array(tile_img_pil)[..., :3]
        tile_cells = seg_model.detect(tile_img_np, (min_x, min_y))

        if params.tissue_filter:
            tile_cells = [
                tile_cell
                for tile_cell in tile_cells
                if utils.overlaps_with_mask(tile_cell, tile_tissue_mask)
            ]

        tile_id_to_cells[tile_id] = tile_cells

        all_cells += tile_cells

    if params.save_to_cache:
        os.makedirs(cache_path, exist_ok=True)

        print(f"saving cache to {cache_path}")
        compression_kwarg = {}
        with gzip.open(
            utils.linux_path(cache_path, "tile_id_to_cells.json.gz"),
            mode="wb",
            # encoding="utf-8",
            **compression_kwarg,
        ) as fid:

            json_b = orjson.dumps(
                tile_id_to_cells,
                option=orjson.OPT_SERIALIZE_NUMPY
                | orjson.OPT_PASSTHROUGH_DATETIME
                | orjson.OPT_NON_STR_KEYS
                | orjson.OPT_INDENT_2,
            )
            fid.write(json_b)

    if tile_id_to_cells:
        utils.remove_duplicates_from_tiles(
            wsi,
            tile_id_to_wsi_bbox,
            tile_id_to_cells,
            overlapping_tiles,
            params.nms_thresh,
            params.vis,
        )

    features = utils.save_cells_as_qupath_geojson(
        all_cells,
        out_path,
        label_map,
        min_area=params.min_area,
        chunk_size=0,
        output_wsi_name=wsi_name,
    )
    return features


def classify_wsi(
    cls_model,
    seg_model,
    wsi_file,
    seg_output_path,
    cls_output_path,
    wsi_file_name,
    cls_cache_path,
):
    seg_cache_path = utils.linux_path(cls_cache_path, "seg.geojson.gz")

    if os.path.isfile(seg_cache_path):
        print(f"loading cls seg cache from {seg_cache_path}")
        with gzip.open(
            seg_cache_path,
            mode="rb",
        ) as fid:
            seg_data = orjson.loads(
                fid.read(),
            )
        polygons = seg_data["polygons"]
        classes = seg_data["classes"]
        features = seg_data["features"]
    else:
        assert os.path.exists(
            seg_output_path
        ), f"Nonexistent segmentation output path: {seg_output_path}"

        labels = list(set(list(seg_model.label_map.values()) + cls_model.class_names))
        polygons, classes, features = utils.load_detections_from_qupath_geojson(
            seg_output_path, labels
        )
        seg_data = dict(
            polygons=polygons,
            classes=classes,
            features=features,
        )
        print(f"saving cls seg cache to {seg_cache_path}")
        with gzip.open(
            seg_cache_path,
            mode="wb",
        ) as fid:
            json_b = orjson.dumps(
                seg_data,
                option=orjson.OPT_SERIALIZE_NUMPY
                | orjson.OPT_PASSTHROUGH_DATETIME
                | orjson.OPT_NON_STR_KEYS
                | orjson.OPT_INDENT_2,
            )
            fid.write(json_b)

    nuclei_classes = cls_model.classify(wsi_file, polygons, cls_cache_path)

    assert len(nuclei_classes) == len(features), "nuclei_classes len mismatch"
    for feat, class_info in zip(features, nuclei_classes, strict=True):
        feat["properties"]["classification"]["name"] = class_info["cls"]
        feat["properties"]["classification"]["conf"] = class_info["conf"]

    print(f"saving classification results to: {cls_output_path}")
    os.makedirs(cls_output_path, exist_ok=True)
    utils.save_geojson_as_chunks(
        features, chunk_size=0, out_path=cls_output_path, output_wsi_name=wsi_file_name
    )

    return features


def annotations_geojson_to_mask(
    ann_path,
    mask_path,
    mask_h,
    mask_w,
):

    features = utils.load_geojson_as_chunks(ann_path)

    mask = np.zeros((mask_h, mask_w), dtype=np.uint8)
    # assert len(features) < len(all_rgb_cols), "too many cells for 8 bit RGB image"

    n_features = len(features)
    for feat_id, feat in tqdm(
        enumerate(features), desc="writing annotations to mask", total=n_features
    ):
        feat_properties = feat["properties"]
        if feat_properties["objectType"] != "annotation":
            continue

        geom = shapely.geometry.shape(feat["geometry"])
        if geom.geom_type == "MultiPolygon":
            for geom_ in geom.geoms:
                utils.draw_geom_to_mask(geom_, mask, col_id=255)
        else:
            utils.draw_geom_to_mask(geom, mask, col_id=255)

    print(f"saving mask to {mask_path}")
    tifffile.imwrite(
        mask_path,
        mask,
        bigtiff=True,
        compression="zlib",
        photometric=None,
        metadata=None,
    )


def export_qp_annotations(params: Params, wsi_path, output_path):
    assert params.qp_exe, "qp_exe must be provided"
    assert params.qp_dir, "qp_dir must be provided"
    assert params.qp_export_script, "qp_export_script must be provided"
    assert params.qp_proj_path, "qp_proj_path must be provided"

    script_dir_path = str(Path(__file__).resolve().parent)
    groovy_script_path = utils.linux_path(script_dir_path, params.qp_dir, params.qp_export_script)
    assert os.path.isfile(groovy_script_path), f"invalid groovy script: {groovy_script_path}"
    qp_cmds = [
        params.qp_exe,
        "script",
        groovy_script_path,
        "--args",
        params.qp_proj_path,
        "--args",
        wsi_path,
        "--args",
        output_path,
    ]

    qp_cmd = utils.to_str(qp_cmds, sep=" ")
    print(f"running qupath export cmd:\n{qp_cmd}")
    try:
        subprocess.run(qp_cmds, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return False


def main():
    params = Params()
    paramparse.process(params)

    # if params.deploy.enable:
    # deploy_model(params)

    assert params.wsi_root_dir, "wsi_root_dir must be provided"
    assert params.wsi_dir, "wsi_dir must be provided"

    wsi_dir_path = utils.linux_path(params.wsi_root_dir, params.wsi_dir)

    wsi_files = utils.get_wsi_files(
        wsi_dir_path,
        params.wsi_exts,
        params.recursive,
        params.filter,
    )
    tiles_dirs = utils.get_tiles_dirs(
        params.tiles_root_dir, params.tiles_dirs, params.recursive, params.filter
    )

    n_wsi_files = len(wsi_files)
    n_tiles_dirs = len(tiles_dirs)

    if n_wsi_files != n_tiles_dirs:
        open("wsi_files.log", "w").write(utils.to_str(wsi_files))
        open("tiles_dirs.log", "w").write(utils.to_str(tiles_dirs))
        raise AssertionError(
            f"mismatch between n_wsi_files ({n_wsi_files}) and n_tiles_dirs ({n_tiles_dirs})"
        )

    # wsi_file_names = [os.path.splitext(os.path.basename(wsi_file))[0] for wsi_file in wsi_files]
    # tiles_dir_names = [os.path.basename(tiles_dir) for tiles_dir in tiles_dirs]

    print(f"Running on {n_wsi_files} WSI(s):\n{utils.to_str_multi([wsi_files, tiles_dirs])}\n")

    assert params.output_root_dir, "output_root_dir must be provided"

    cls_model = get_cls_model(params.cls, params)

    for model_id, model_name in enumerate(params.models):

        seg_model: CellSegWSIBase = get_seg_model(model_name, params)

        label_map = copy.deepcopy(seg_model.label_map)

        for wsi_file_id, (
            wsi_file,
            tiles_dir,
        ) in enumerate(zip(wsi_files, tiles_dirs, strict=True)):
            wsi_file_name = utils.path_to_name(wsi_file)

            assert wsi_file_name, "wsi_file_name cannot be empty"

            print(f"\n\nannotating wsi {wsi_file_id+1} / {n_wsi_files}: {wsi_file_name}")

            wsi_parent_dir = utils.path_to_parent(wsi_file)

            tissue_mask_file = utils.linux_path(
                wsi_parent_dir, params.mask_dir, wsi_file_name + params.mask_ext
            )
            tissue_annotation_file = utils.linux_path(
                wsi_parent_dir, params.ann_dir, wsi_file_name + params.ann_ext
            )

            output_dir = utils.linux_path(params.output_root_dir, params.wsi_dir)
            os.makedirs(output_dir, exist_ok=True)

            seg_output_path = params.seg_output_path
            if not seg_output_path:
                seg_output_path = utils.linux_path(output_dir, seg_model.name, "seg")
                if wsi_parent_dir != wsi_dir_path:
                    wsi_parent_dir_relative = os.path.relpath(wsi_parent_dir, wsi_dir_path)
                    seg_output_path = utils.linux_path(seg_output_path, wsi_parent_dir_relative)

            seg_cache_path = utils.linux_path(
                output_dir, ".cache", seg_model.name, "seg", f"{wsi_file_name}"
            )

            if params.qp_export and not os.path.isfile(tissue_annotation_file):
                if not export_qp_annotations(params, wsi_file, tissue_annotation_file):
                    raise AssertionError("annotations exporting from QP project failed")

            if not os.path.isfile(tissue_mask_file):
                wsi = openslide.OpenSlide(wsi_file)
                wsi_w, wsi_h = wsi.dimensions
                wsi.close()
                annotations_geojson_to_mask(
                    tissue_annotation_file,
                    tissue_mask_file,
                    wsi_h,
                    wsi_w,
                )

            if params.skip_seg:
                print("skipping segmentation")
            else:
                segment_wsi(
                    params,
                    seg_model,
                    wsi_file,
                    tiles_dir,
                    tissue_mask_file,
                    tissue_annotation_file,
                    seg_output_path,
                    seg_cache_path,
                    label_map,
                )

            if cls_model is not None:
                cls_cache_path = utils.linux_path(
                    output_dir, ".cache", seg_model.name, cls_model.name, f"{wsi_file_name}"
                )
                os.makedirs(cls_cache_path, exist_ok=True)

                cls_output_path = params.cls_output_path
                if not cls_output_path:
                    cls_output_path = utils.linux_path(output_dir, seg_model.name, cls_model.name)
                print(f"cls_output_path: {cls_output_path}")
                classify_wsi(
                    cls_model,
                    seg_model,
                    wsi_file,
                    seg_output_path,
                    cls_output_path,
                    wsi_file_name,
                    cls_cache_path,
                )


if __name__ == "__main__":
    main()
