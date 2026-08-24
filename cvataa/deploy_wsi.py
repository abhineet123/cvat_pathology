import os
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
import paramparse

from cell_seg_wsi import CellSegWSIBase

from create_tissue_mask import burn_polygons_tiled

from annotate_wsi import (
    Params as BaseParams,
    segment_wsi,
    classify_wsi,
    get_seg_model,
    get_cls_model,
)

import cell_seg_utils as utils


class Params(BaseParams):
    def __init__(self):
        BaseParams.__init__(self)
        """
        settings for deploying WSI annotation model as a background service
        monitoring a shared folder for new WSIs to process

        :ivar poll_interval: time interval in secs between successive polling of the shared folder to check for new WSI files
        :ivar copy_wait_t: time in secs to wait for WSI file size to change before deciding that the copy operation is complete
        :ivar max_days: Maximum number of past days whose images are to be monitored
        """

        self.root_path = ""
        self.cache_path = ""
        self.log_path = ""
        self.qp_suffix = "QP"
        self.annotations_dir = "annotations"
        self.masks_dir = "masks"
        self.out_dir = "detections"

        # self.magee_dir = "magee"
        self.magee_dir = ""

        self.qp_exe = "QuPath"
        self.qp_dir = "qupath"
        self.qp_script = "import_annotations_headless.groovy"

        self.dab_thresholds = [0.09, 0.29, 0.49]
        self.assay_types = []

        self.wsi_ext = ".svs"
        self.ann_ext = ".geojson.gz"
        self.mask_ext = ".tiff"

        self.poll_interval = 10
        self.copy_wait_t = 10
        self.max_days = 0
        self.verbose = 0
        self.time_fmt = "%y%m%d_%H%M%S"
        self.date_fmt = "%Y_%m_%d"


def custom_color_deconvolution(rgb, stain_matrix):
    # Perform color deconvolution (converting RGB to stain optical densities)
    # stadt_matrix inverse is used to separate channels

    from skimage import img_as_float

    rgb = img_as_float(rgb)

    # Avoid log(0) by adding a small epsilon
    rgb_safe = np.clip(rgb, 0.05, 1.0)

    """
    https://forum.image.sc/t/how-does-detection-of-positive-dab-stained-cells-work-in-qupath-precisely/94571
    """
    # Convert RGB to Optical Density (OD)
    od = -np.log(rgb_safe)
    # Solve unmixing matrix
    inv_matrix = np.linalg.inv(stain_matrix)
    # Dot product to separate stain concentrations
    stain_densities = np.dot(od.reshape((-1, 3)), inv_matrix)

    return stain_densities.reshape(rgb.shape)


def rgb_to_od_dab_skimage(patch_rgb):
    import numpy as np
    from skimage import img_as_float

    patch_rgb_norm = img_as_float(patch_rgb)

    """Note: skimage has built-in rgb2hed for H&E, but custom matrix is needed for H-DAB"""
    from skimage.color import rgb2hed

    """https://scikit-image.org/docs/stable/api/skimage.color.html#skimage.color.separate_stains"""
    from skimage.color import separate_stains, hed_from_rgb, hdx_from_rgb

    separated_stains = separate_stains(patch_rgb_norm, hed_from_rgb)

    # hematoxylin_channel = separated_stains[:, :, 0]
    dab_channel = separated_stains[:, :, 2]
    return dab_channel


def rgb_to_od_dab_manual(rgb):
    HEMATOXYLIN = np.array([0.6511078257574492, 0.7011930431234068, 0.29049426072255424])
    DAB = np.array([0.2691668720495607, 0.5682411743268503, 0.7775931859209531])
    BACKGROUND = np.array([255.0, 255.0, 255.0])

    def _build_stain_matrix():
        """Third vector is the cross product of the first two (QuPath's
        convention for a 2-stain setup), giving an invertible 3x3."""
        h = HEMATOXYLIN / np.linalg.norm(HEMATOXYLIN)
        d = DAB / np.linalg.norm(DAB)
        r = np.cross(h, d)
        n = np.linalg.norm(r)
        r = r / n if n > 1e-9 else np.array([0.0, 0.0, 1.0])
        return np.linalg.inv(np.stack([h, d, r]))

    STAIN_INV = _build_stain_matrix()

    """RGB uint8 -> (hematoxylin, dab) optical density channels."""
    rgb = np.maximum(rgb.astype(np.float64), 1.0)  # avoid log(0)
    od = -np.log10(rgb / BACKGROUND[None, None, :])
    stains = (od.reshape(-1, 3) @ STAIN_INV).reshape(od.shape)

    hematoxylin_channel = stains[..., 0]
    dab_channel = stains[..., 1]
    return dab_channel


def get_mean_dab_od_for_nucleus(wsi, coords):
    coords = np.asarray(coords, dtype=np.int32).squeeze()
    xs, ys = coords[:, 0], coords[:, 1]
    min_x, max_x = np.amin(xs), np.amax(xs)
    min_y, max_y = np.amin(ys), np.amax(ys)

    w = max_x - min_x
    h = max_y - min_y

    if w <= 1 or h <= 1:
        return 0

    patch_pil = wsi.read_region(location=(min_x, min_y), level=0, size=(w, h))
    patch_rgb = np.array(patch_pil)[..., :3]

    # patch_dab = rgb_to_od_dab_skimage(patch_rgb)
    patch_dab = rgb_to_od_dab_manual(patch_rgb)

    patch_mask = np.zeros((h, w), dtype=np.uint8)
    patch_coords = np.asarray(coords - [min_x, min_y], dtype=np.int32)
    cv2.fillPoly(patch_mask, [patch_coords], color=255)
    patch_mask_bool = patch_mask.astype(bool)

    nucleus_dab = patch_dab[patch_mask_bool]
    mean_dab = nucleus_dab.mean()
    return mean_dab


def compute_dab_score(wsi_path, features, thresholds, assay_type):

    weak_threshold, moderate_threshold, strong_threshold = thresholds
    n_negative = 0
    n_weak = 0
    n_moderate = 0
    n_strong = 0

    slide = openslide.OpenSlide(wsi_path)

    for feat in features:
        feat_properties = feat["properties"]
        class_info = feat_properties["classification"]

        if class_info["name"] != "Tumor":
            continue

        coords = feat["geometry"]["coordinates"]
        dab = get_mean_dab_od_for_nucleus(slide, coords)

        if dab < weak_threshold:
            n_negative += 1
        elif dab < moderate_threshold:
            n_weak += 1
        elif dab < strong_threshold:
            n_moderate += 1
        else:
            n_strong += 1

    n_total = float(n_negative + n_weak + n_moderate + n_strong)

    if n_total == 0:
        magee_score = 0
    else:
        if assay_type in ["ER", "PR"]:
            magee_score = (
                (float(n_weak) / n_total)
                + (2 * float(n_moderate) / n_total)
                + (3 * float(n_strong) / n_total)
            ) * 100
        else:
            # Ki67 %
            magee_score = float(n_weak + n_moderate + n_strong) / n_total * 100
    return magee_score


def tissue_annotation_to_mask(wsi_path, annotation_path, out_path, verbose):
    wsi_path = Path(wsi_path)

    slide = openslide.OpenSlide(wsi_path)
    wsi_w, wsi_h = slide.dimensions
    slide.close()

    features = utils.load_geojson_as_chunks(annotation_path, verbose=verbose)

    polygons = []
    for feat in features:
        try:
            if feat["properties"]["objectType"] != "annotation":
                continue
        except KeyError:
            pass
        geom = shapely.geometry.shape(feat["geometry"])
        if not geom.is_valid:
            geom = geom.buffer(0)
        polygons.append(geom)

    wsi_mask = burn_polygons_tiled(
        polygons,
        wsi_w,
        wsi_h,
        wsi_out_path=None,
        internal_tile_size=4096,
        memmap=0,
        verbose=0,
    )

    tifffile.imwrite(
        out_path,
        wsi_mask,
        bigtiff=True,
        tile=(512, 512),
        photometric="minisblack",
        compression="zstd",
        compressionargs={"level": 1},
    )


def run_on_wsi(
    params: Params, seg_model, cls_model, wsi_file, ann_file, out_path, assay_type, logger
):
    assert assay_type in ["ER", "PR", "KI67"], f"invalid assay_type: {assay_type}"

    wsi_file_name = utils.path_to_name(wsi_file, remove_ext=True)

    mask_out_dir = utils.linux_path(out_path, params.masks_dir)
    os.makedirs(mask_out_dir, exist_ok=True)

    seg_out_dir_path = utils.linux_path(out_path, params.out_dir)
    seg_cache_dir_path = utils.linux_path(params.cache_path, ".cache", seg_model.name)

    if cls_model is not None:
        seg_out_dir_path = utils.linux_path(seg_out_dir_path, "seg")
        seg_cache_dir_path = utils.linux_path(seg_cache_dir_path, "seg")

    seg_cache_dir_path = utils.linux_path(seg_cache_dir_path, wsi_file_name)

    os.makedirs(seg_out_dir_path, exist_ok=True)
    os.makedirs(seg_cache_dir_path, exist_ok=True)

    label_map = copy.deepcopy(seg_model.label_map)
    label_names = list(label_map.keys())

    if params.skip_seg:
        assert cls_model is not None, "can't skip segmentation without a classifier"
        print("skipping segmentation")
    else:
        mask_out_path = utils.linux_path(mask_out_dir, wsi_file_name + params.mask_ext)
        tissue_annotation_to_mask(wsi_file, ann_file, mask_out_path, verbose=params.verbose)

        features = segment_wsi(
            params=params,
            seg_model=seg_model,
            wsi_file=wsi_file,
            tiles_dir=None,
            tissue_mask_file=mask_out_path,
            tissue_annotation_file=ann_file,
            out_path=seg_out_dir_path,
            cache_path=seg_cache_dir_path,
            label_map=label_map,
        )

    if cls_model is not None:
        cls_cache_dir_path = utils.linux_path(
            params.cache_path, ".cache", seg_model.name, cls_model.name, wsi_file_name
        )
        os.makedirs(cls_cache_dir_path, exist_ok=True)
        cls_out_dir_path = utils.linux_path(out_path, params.out_dir)
        seg_out_json_path = utils.linux_path(seg_out_dir_path, f"{wsi_file_name}{params.ann_ext}")

        label_names = cls_model.class_names
        features = classify_wsi(
            cls_model=cls_model,
            seg_model=seg_model,
            wsi_file=wsi_file,
            seg_output_path=seg_out_json_path,
            cls_output_path=cls_out_dir_path,
            wsi_file_name=wsi_file_name,
            cls_cache_path=cls_cache_dir_path,
        )

    if params.qp_exe:
        assert params.qp_script, "qupath_script must be provided"
        script_dir_path = str(Path(__file__).resolve().parent)
        groovy_script_path = utils.linux_path(script_dir_path, params.qp_dir, params.qp_script)
        assert os.path.isfile(groovy_script_path), f"invalid groovy script: {groovy_script_path}"
        qp_cmds = [
            params.qp_exe,
            "script",
            groovy_script_path,
            "--args",
            out_path,
            "--args",
            wsi_file,
        ]
        logger.info(f"running qupath cmd: {qp_cmds}")
        subprocess.call(qp_cmds)

    if params.magee_dir:
        assert "Tumor" in label_names, "label_names must have Tumor to compute magee scores"

        magee_out_dir_path = utils.linux_path(out_path, params.magee_dir)
        os.makedirs(magee_out_dir_path, exist_ok=True)
        magee_out_path = utils.linux_path(magee_out_dir_path, f"{assay_type}.txt")

        assert params.dab_thresholds, "dab_thresholds must be provided"
        dab_score = compute_dab_score(wsi_file, features, params.dab_thresholds, assay_type)

        if assay_type in ["ER", "PR"]:
            logger.info(f"{assay_type} H-Score: {dab_score:.3f}")
        else:
            logger.info(f"KI67 %: {dab_score:.3f}")

        with open(magee_out_path, "w") as fid:
            fid.write(f"{dab_score:.3f}")

    return True


def process_wsi(
    params: Params,
    seg_model,
    cls_model,
    wsi_log: dict,
    wsi_path,
    ann_path,
    out_path,
    assay_type,
    logger,
):
    wsi_stat = Path(wsi_path).stat()
    wsi_mod_t = datetime.fromtimestamp(wsi_stat.st_mtime)

    ann_stat = Path(ann_path).stat()
    ann_mod_t = datetime.fromtimestamp(ann_stat.st_mtime)

    shared_name = utils.path_to_name(wsi_path, remove_ext=False)

    if shared_name in wsi_log:
        file_dict = wsi_log[shared_name]
        run_timestamps = file_dict["run_timestamps"]
        prev_run_t = datetime.strptime(run_timestamps[-1], params.time_fmt)
        if prev_run_t > wsi_mod_t and prev_run_t > ann_mod_t:
            """latest versions of the WSI and GeoJSON have already been processed"""
            return False
    else:
        file_dict = dict(run_timestamps=[])

    utils.wait_for_file_to_finalize(wsi_path, params.copy_wait_t, wsi_mod_t, params.verbose)
    utils.wait_for_file_to_finalize(ann_path, params.copy_wait_t, ann_mod_t, params.verbose)

    print("\n")

    logger.info(f"running on WSI: {wsi_path}")

    if not run_on_wsi(
        params=params,
        seg_model=seg_model,
        cls_model=cls_model,
        wsi_file=wsi_path,
        ann_file=ann_path,
        out_path=out_path,
        assay_type=assay_type,
        logger=logger,
    ):
        logger.error("run failed")
        return False

    file_dict["run_timestamps"].append(datetime.now().strftime(params.time_fmt))
    wsi_log[shared_name] = file_dict

    print("\n")

    return True


def get_patient_log(patient_dir, day_dir, wsi_log, time_fmt):
    name_split = patient_dir.name.split("-")
    if name_split[-1] in ["D", "L"]:
        accession_id = "-".join(name_split[:-1])
    else:
        accession_id = patient_dir.name

    if accession_id in wsi_log:
        patient_dict = wsi_log[accession_id]
    else:
        timestamp = datetime.now().strftime(time_fmt)
        patient_dict = wsi_log[accession_id] = dict(
            day=day_dir.name,
            timestamp=timestamp,
            accession_id=accession_id,
            wsi={},
        )

    return patient_dict


def main():
    params = Params()
    paramparse.process(params)

    assert len(params.models) == 1, "deployment mode can be run with only one model"

    assert params.root_path, "deployment root_path must be provided"
    assert params.log_path, "log_path must be provided"

    os.makedirs(params.log_path, exist_ok=True)

    timestamp = datetime.now().strftime(params.time_fmt)
    term_log_path = utils.linux_path(params.log_path, f"deploy-{timestamp}.log")
    logger = utils.init_logger(term_log_path)

    json_log_path = utils.linux_path(params.log_path, f"deploy_wsi.json")
    if os.path.exists(json_log_path):
        logger.info(f"loading json_log from {json_log_path}")
        with open(json_log_path, "r") as fid:
            json_log: dict = json.load(fid)
    else:
        logger.info(f"saving json_log to {json_log_path}")
        json_log = {}

    seg_model: CellSegWSIBase = get_seg_model(params.models[0], params)
    cls_model = get_cls_model(params.cls, params)

    if not params.cache_path:
        params.cache_path = params.root_path

    while True:
        if params.verbose:
            print()

        day_dirs = [
            f
            for f in os.scandir(params.root_path)
            if f.is_dir() and not f.name.startswith(".") and utils.is_date(f.name, params.date_fmt)
        ]
        day_dirs.sort(key=utils.path_to_name, reverse=True)

        n_days = len(day_dirs)
        if n_days > params.max_days > 0:
            day_dirs = day_dirs[: params.max_days]
            n_days = len(day_dirs)

        patients_dirs = [
            (p, d, get_patient_log(p, d, json_log, params.time_fmt))
            for d in day_dirs
            for p in os.scandir(d.path)
            if p.is_dir()
        ]
        log_updated = False

        if params.verbose:
            pbar = tqdm(patients_dirs, desc="checking for updates", ncols=100)
        else:
            pbar = patients_dirs

        for patient_dir, day_dir, patient_log in pbar:
            accession_id = patient_log["accession_id"]
            qp_proj_path = utils.linux_path(patient_dir.path, f"{accession_id}-{params.qp_suffix}")
            if not os.path.isdir(qp_proj_path):
                continue

            ann_dir_path = utils.linux_path(qp_proj_path, params.annotations_dir)
            if not os.path.isdir(ann_dir_path):
                continue

            wsi_paths = [
                utils.linux_path(patient_dir.path, f"{accession_id}-{assay_type}{params.wsi_ext}")
                for assay_type in params.assay_types
            ]
            ann_paths = [
                utils.linux_path(ann_dir_path, f"{accession_id}-{assay_type}{params.ann_ext}")
                for assay_type in params.assay_types
            ]
            patient_wsis_anns = [
                (wsi_path, ann_path, assay_type)
                for wsi_path, ann_path, assay_type in zip(
                    wsi_paths, ann_paths, params.assay_types, strict=True
                )
                if os.path.exists(wsi_path) and os.path.exists(ann_path)
            ]
            for wsi, ann, assay_type in patient_wsis_anns:
                if process_wsi(
                    params=params,
                    seg_model=seg_model,
                    cls_model=cls_model,
                    wsi_log=patient_log["wsi"],
                    wsi_path=wsi,
                    ann_path=ann,
                    out_path=qp_proj_path,
                    assay_type=assay_type,
                    logger=logger,
                ):
                    log_updated = True

        if log_updated:
            with open(json_log_path, "w") as fid:
                json.dump(json_log, fid, indent=4)

        if params.verbose:
            for _ in tqdm(range(params.poll_interval), desc="sleeping between checks", ncols=100):
                time.sleep(1)
            print()
        else:
            time.sleep(params.poll_interval)


if __name__ == "__main__":
    main()
