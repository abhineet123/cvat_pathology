from tqdm import tqdm
import os
import shutil
import time

from datetime import datetime
from pathlib import Path
import json
import subprocess
import numpy as np

import cv2
import openslide

import paramparse

import cell_seg_utils as utils


class Params(paramparse.CFG):
    """
    :ivar poll_interval: time interval in secs between successive polling of the shared folder to check for new WSI files
    :ivar copy_wait_t: time in secs to wait for WSI file size to change before deciding that the copy operation is complete
    :ivar past_days: number of previous days to monitor for changes on the shared folder for synchronization to the local folder
    """

    def __init__(self):
        paramparse.CFG.__init__(self, cfg_prefix="sync")
        self.shared_cfg = ""
        # self.shared_cfg = "sync.cfg"

        self.shared_root = ""
        self.local_root = ""
        self.log_path = ""
        self.assays = [
            "HE",
            "ER",
            "PR",
            "KI67",
        ]
        self.wsi_ext = ".svs"
        self.label_ext = ".png"
        self.ann_ext = ".geojson.gz"

        self.qupath_suffix = "QP"
        self.annotations_dir = "annotations"

        self.qp_sync = 0
        self.qp_create = 0

        self.qp_exe = "QuPath"
        self.qp_dir = "qupath"
        self.qp_create_script = "create_project_headless.groovy"
        self.qp_sync_script = "sync_filenames_headless.groovy"

        self.start_time = 00
        self.end_time = 24
        self.verbose = 0

        self.poll_interval = 10
        self.fin_wait_t = 10
        self.start_wait_t = 0

        self.max_months = 2
        self.max_days = 30
        self.failed_suffixes = [
            "FAILED",
        ]
        self.block_suffixes = ["A1", "A2"]

        self.time_fmt = "%y%m%d_%H%M%S"
        self.date_fmt = "%Y-%m-%d"
        self.month_fmt = "%Y-%m"


def copy_dir_with_rsync(src, dst, exclusion=None):
    cmds = [
        "rsync",
        "-a",
    ]
    if exclusion is not None:
        cmds += ["--exclude", exclusion]
    cmds += [src, dst]

    subprocess.run(cmds)


def copy_file_with_rsync(src, dst):
    subprocess.run(["rsync", "--info=progress2", src, dst])


def create_qp_project(params: Params, qp_proj_path, dst_path_to_src_name, logger):
    print(f"Creating QuPath project: {qp_proj_path}")

    assert params.qp_exe, "qupath exe must be provided"
    assert params.qp_create_script, "qupath_script must be provided"
    script_dir_path = str(Path(__file__).resolve().parent)
    groovy_script_path = utils.linux_path(script_dir_path, params.qp_dir, params.qp_create_script)
    assert os.path.isfile(groovy_script_path), f"invalid groovy script: {groovy_script_path}"
    qp_cmds = [
        params.qp_exe,
        "script",
        groovy_script_path,
        "--args",
        qp_proj_path,
    ]
    for dst_path, src_name in dst_path_to_src_name.items():
        dst_name = utils.path_to_name(dst_path, remove_ext=False)
        qp_cmds += ["--args", f"{dst_name}---{src_name}"]

    qp_cmd = utils.to_str(qp_cmds, sep=" ")
    logger.info(f"running qupath create command:\n{qp_cmd}")
    try:
        subprocess.run(qp_cmds, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return False


def sync_qp_image_names(params: Params, qp_proj_path, logger):
    assert params.qp_exe, "qp_exe must be provided"
    assert params.qp_sync_script, "qp_sync_script must be provided"
    script_dir_path = str(Path(__file__).resolve().parent)
    groovy_script_path = utils.linux_path(script_dir_path, params.qp_dir, params.qp_sync_script)
    assert os.path.isfile(groovy_script_path), f"invalid groovy script: {groovy_script_path}"
    qp_cmds = [
        params.qp_exe,
        "script",
        groovy_script_path,
        "--args",
        qp_proj_path,
        "--args",
        params.shared_root,
        "--args",
        params.local_root,
    ]

    qp_cmd = utils.to_str(qp_cmds, sep=" ")
    logger.info(f"running qupath sync cmd:\n{qp_cmd}")
    try:
        subprocess.run(qp_cmds, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return False


def sync_dir(params: Params, shared_dir: str, exclusion=None):
    assert shared_dir.startswith(params.shared_root), "src_path does not start with shared_root"
    dst_path = shared_dir.replace(params.shared_root, params.local_root)
    dst_parent_dir = os.path.dirname(dst_path)

    copy_dir_with_rsync(shared_dir, dst_parent_dir, exclusion)


def is_previously_copied(file_dict: dict, shared_path: str, time_fmt: str):
    file_stat = Path(shared_path).stat()
    modification_t = datetime.fromtimestamp(file_stat.st_mtime)
    prev_copied_t = datetime.strptime(file_dict["copied_at"], time_fmt)
    if prev_copied_t > modification_t:
        """latest version of the file has already been copied"""
        # local_file = shared_file.replace(params.shared_root, params.local_root)
        # assert os.path.exists(
        #     local_file
        # ), f"local_file exists in files_info but not on disk: {local_file}"
        return True
    return False


def sync_file(params: Params, files_info: dict, shared_path: str, logger, orig_name=None):

    shared_name = utils.path_to_name(shared_path, remove_ext=False)
    if shared_name in files_info:
        file_dict = files_info[shared_name]
        if is_previously_copied(file_dict, shared_path, params.time_fmt):
            return False
    else:
        files_info[shared_name] = file_dict = dict()

    utils.wait_for_file_to_finalize(shared_path, params.fin_wait_t, params.verbose)

    logger.info(f"copying to workstation: {shared_path}")

    local_wsi_path = copy_file_to_local(shared_path, params.shared_root, params.local_root, logger)
    if local_wsi_path is None:
        logger.error("file copy failed")
        return False

    file_dict["shared_path"] = shared_path
    # file_dict["local_path"] = local_wsi_path
    file_dict["name"] = shared_name
    file_dict["size"] = os.path.getsize(shared_path)
    file_dict["copied_at"] = datetime.now().strftime(params.time_fmt)

    if orig_name is not None:
        file_dict["orig_name"] = orig_name
    return True


def copy_file_to_local(src_path: str, shared_root: str, local_root: str, logger):
    assert src_path.startswith(shared_root), "src_path does not start with shared_root"

    dst_path = src_path.replace(shared_root, local_root)

    dst_dir = os.path.dirname(dst_path)

    if os.path.isfile(dst_path):
        os.remove(dst_path)

    os.makedirs(dst_dir, exist_ok=True)

    copy_file_with_rsync(src_path, dst_path)

    if not os.path.isfile(dst_path):
        logger.error(f"copied file does not exist: {dst_path}")
        return None

    if os.path.getsize(src_path) != os.path.getsize(dst_path):
        logger.error("copied file size mismatch")
        return None

    return dst_path


def delete_failed_patients_from_ws(shared_root, local_root, failed_dirs, logger):
    for failed_dir in failed_dirs:
        shared_path = failed_dir.path
        failed_suffix = failed_dir.name.split("-")[-1]

        ws_path = shared_path.replace(shared_root, local_root)
        if os.path.exists(ws_path):
            logger.info(f"deleting failed patient from workstation: {ws_path}")
            shutil.rmtree(ws_path)


def get_patient_info(patient_dir, day_dir, month_dir, wsi_log, time_fmt):
    name_split = patient_dir.name.split("-")
    if name_split[-1] in ["D", "L"]:
        accession_id = "-".join(name_split[:-1])
    else:
        accession_id = patient_dir.name

    if accession_id in wsi_log:
        patient_dict = wsi_log[accession_id]
        if "wsi" not in patient_dict:
            patient_dict["wsi"] = {}
        if "annotations" not in patient_dict:
            patient_dict["annotations"] = {}
    else:
        timestamp = datetime.now().strftime(time_fmt)
        patient_dict = wsi_log[accession_id] = dict(
            month=month_dir.name,
            day=day_dir.name,
            timestamp=timestamp,
            accession_id=accession_id,
            wsi={},
            annotations={},
        )

    return patient_dict


def save_wsi_meta_images(patient_dir, accession_id, wsi_path, assay, label_ext):
    wsi = openslide.OpenSlide(wsi_path)
    associated_images = wsi.associated_images

    label_dir_path = utils.linux_path(patient_dir, f"{accession_id}-meta")
    os.makedirs(label_dir_path, exist_ok=True)

    # labels = []
    # label_images = []
    for label in associated_images:
        image = associated_images[label]
        rgb_img = image.convert("RGB")
        image_np = np.asarray(rgb_img)
        image_np = utils.annotate(
            image_np,
            assay,
            fmt=utils.CVText(
                color="white",
                bkg_color="black",
                location=0,
                font=3,
                size=1.5,
                thickness=1,
                line_type=2,
                offset=(5, 50),
            ),
        )
        # label_images.append(image_np)
        # labels.append(label)
        label_name = f"{label}-{assay}{label_ext}"
        label_file_path = utils.linux_path(label_dir_path, label_name)
        cv2.imwrite(label_file_path, image_np)


def rename_file(params: Params, patient_dir, src_name, dst_name):
    print(f"renaming {src_name} >> {dst_name}")

    src_path = utils.linux_path(patient_dir, src_name)
    dst_path = utils.linux_path(patient_dir, dst_name)

    utils.wait_for_file_to_finalize(src_path, params.fin_wait_t, params.verbose)

    os.rename(src_path, dst_path)

    assert os.path.isfile(dst_path), "renaming failed"

    return dst_path


def is_valid_scanned_wsi_name(filename, wsi_ext=".svs"):
    if not filename.endswith(wsi_ext):
        return False

    try:
        barcode, scan_time = filename.split("_")
    except ValueError:
        return False

    return True


def process_wsi_files_v2(
    params: Params, patient_info, patient_dir, accession_id, qp_proj_path, logger
):
    patient_wsis = [
        f
        for f in os.scandir(patient_dir)
        if f.is_file() and is_valid_scanned_wsi_name(f.name, params.wsi_ext)
    ]
    if len(patient_wsis) < len(params.assays):
        return False

    for patient_wsi, assay in zip(patient_wsis, params.assays, strict=True):
        save_wsi_meta_images(patient_dir, accession_id, patient_wsi.path, assay, params.label_ext)

    if params.start_wait_t > 0:
        patient_name = utils.path_to_name(patient_dir)
        utils.sleep_with_pbar(
            params.start_wait_t, f"waiting before processing WSIs for {patient_name}"
        )

        if any(not f.is_file() for f in patient_wsis):
            """
            names and/or existence of WSI files changed on disk between the start and end of waiting period
            so we re-process this patient in the next round of checks
            """
            return False

    barcodes, scan_times = zip(*[f.name.split("_") for f in patient_wsis])

    barcodes_sort_indices = sorted(range(len(barcodes)), key=lambda i: barcodes[i])
    scan_times_sort_indices = sorted(range(len(scan_times)), key=lambda i: scan_times[i])

    src_to_dst_names = {}
    dst_path_to_src_name = {}

    for file_id, assay in zip(scan_times_sort_indices, params.assays, strict=True):
        src_name = patient_wsis[file_id].name
        dst_name = f"{accession_id}-{assay}{params.wsi_ext}"

        dst_path = rename_file(params, patient_dir, src_name, dst_name)

        # n_labels = len(label_images)
        # label_image = utils.stack_images(label_images, grid_size=(1, n_labels))
        # cv2.imwrite(label_file_path, label_image)

        src_to_dst_names[src_name] = dst_name
        dst_path_to_src_name[dst_path] = src_name

    if scan_times_sort_indices != barcodes_sort_indices:
        barcode_sorting = [
            f"{patient_wsis[i].name} >> {src_to_dst_names[patient_wsis[i].name]}"
            for i in barcodes_sort_indices
        ]
        scan_time_sorting = [
            f"{patient_wsis[i].name} >> {src_to_dst_names[patient_wsis[i].name]}"
            for i in scan_times_sort_indices
        ]
        warn_file = utils.linux_path(patient_dir, "barcode_scan_time_order_mismatch.txt")
        with open(warn_file, "w") as fid:
            fid.write(f"scan_time_sorting:\n{utils.to_str(scan_time_sorting)}\n\n")
            fid.write(f"barcode_sorting:\n{utils.to_str(barcode_sorting)}\n")

    if not os.path.isdir(qp_proj_path):
        os.makedirs(qp_proj_path)
        if params.qp_create:
            create_qp_project(params, qp_proj_path, dst_path_to_src_name, logger)

    log_updated = False
    for dst_path, src_name in dst_path_to_src_name.items():
        if sync_file(params, patient_info["wsi"], dst_path, logger, src_name):
            log_updated = True

    return log_updated


def process_wsi_files_v1(params: Params, patient_info, patient_dir, accession_id, logger):
    wsi_paths = [
        utils.linux_path(patient_dir.path, f"{accession_id}-{assay_type}{params.wsi_ext}")
        for assay_type in params.assays
    ]
    patient_wsis = [wsi_path for wsi_path in wsi_paths if os.path.exists(wsi_path)]
    for wsi in patient_wsis:
        if sync_file(params, patient_info["wsi"], wsi, logger):
            log_updated = True
    return log_updated


def main():
    params: Params = paramparse.process(Params)

    assert params.shared_root, "shared_path must be provided"
    assert params.local_root, "local_root must be provided"
    assert params.log_path, "log_path must be provided"

    os.makedirs(params.log_path, exist_ok=True)

    json_log_path = utils.linux_path(params.log_path, f"sync_wsi.json")
    if os.path.exists(json_log_path):
        with open(json_log_path, "r") as fid:
            json_log: dict = json.load(fid)
    else:
        json_log = {}

    timestamp = datetime.now().strftime(params.time_fmt)
    term_log_path = utils.linux_path(params.log_path, f"sync_wsi-{timestamp}.log")
    logger = utils.init_logger(term_log_path)

    shared_cfg = (
        utils.linux_path(params.shared_root, params.shared_cfg) if params.shared_cfg else None
    )

    while True:
        if shared_cfg is not None and os.path.isfile(shared_cfg):
            params.cfg = params.cfg_ext = params.cfg_prefix = params.cfg_root = ""
            paramparse.process(params, cfg=shared_cfg, cfg_cache=0)

        if params.verbose:
            print()

        month_dirs = [
            m
            for m in os.scandir(params.shared_root)
            if m.is_dir() and not m.name.startswith(".") and utils.is_date(m.name, params.month_fmt)
        ]
        month_dirs.sort(key=lambda m: m.name, reverse=True)
        n_months = len(month_dirs)
        if n_months > params.max_months > 0:
            month_dirs = month_dirs[: params.max_months]
            n_months = len(month_dirs)

        day_dirs = [
            (d, m)
            for m in month_dirs
            for d in os.scandir(m.path)
            if d.is_dir() and not d.name.startswith(".") and utils.is_date(d.name, params.date_fmt)
        ]
        day_dirs.sort(key=lambda dm: dm[0].name, reverse=True)
        n_days = len(day_dirs)
        if n_days > params.max_days > 0:
            day_dirs = day_dirs[: params.max_days]
            n_days = len(day_dirs)

        patients_dirs = [(p, d, m) for d, m in day_dirs for p in os.scandir(d.path) if p.is_dir()]

        if params.block_suffixes:
            patients_dirs_w_blocks = []
            for p, d, m in patients_dirs:
                block_names = [f"{p.name}-{b}" for b in params.block_suffixes]
                pb_dirs = [pb for pb in os.scandir(p.path) if pb.name in block_names]
                if pb_dirs:
                    patients_dirs_w_blocks += [(pb, d, m) for pb in pb_dirs]
                else:
                    patients_dirs_w_blocks.append((p, d, m))
            patients_dirs = patients_dirs_w_blocks[:]

        if params.failed_suffixes:
            failed_patients_dirs = []
            successful_patients_dirs = []
            for p, d, m in patients_dirs:
                parts = p.name.split("-")
                if parts[-1] in params.failed_suffixes:
                    failed_patients_dirs.append(p)
                else:
                    successful_patients_dirs.append((p, d, m))

            if failed_patients_dirs:
                delete_failed_patients_from_ws(
                    params.shared_root, params.local_root, failed_patients_dirs, logger
                )
                patients_dirs = successful_patients_dirs[:]

        patients_dirs = [
            (p, get_patient_info(p, d, m, json_log, params.time_fmt)) for p, d, m in patients_dirs
        ]
        log_updated = False

        if params.verbose:
            pbar = tqdm(patients_dirs, desc="polling for change", ncols=100)

        for p, patient_info in patients_dirs:
            accession_id = patient_info["accession_id"]

            qp_proj_path = utils.linux_path(p.path, f"{accession_id}-{params.qupath_suffix}")

            wsi_updated = process_wsi_files_v2(
                params, patient_info, p, accession_id, qp_proj_path, logger
            )

            if wsi_updated:
                log_updated = True

            ann_dir_path = utils.linux_path(qp_proj_path, params.annotations_dir)
            if not os.path.isdir(ann_dir_path):
                continue

            ann_paths = [
                utils.linux_path(ann_dir_path, f"{accession_id}-{assay_type}{params.ann_ext}")
                for assay_type in params.assays
            ]
            patient_anns = [ann_path for ann_path in ann_paths if os.path.exists(ann_path)]

            for ann in patient_anns:
                ann_updated = sync_file(params, patient_info["annotations"], ann, logger)
                if ann_updated:
                    if params.qp_sync:
                        sync_qp_image_names(paramparse, qp_proj_path, logger)
                    sync_dir(params, qp_proj_path, exclusion=params.annotations_dir)
                    log_updated = True

            if params.verbose:
                pbar.update(1)

        if log_updated:
            with open(json_log_path, "w") as fid:
                json.dump(json_log, fid, indent=4)

        if params.verbose:
            for _ in tqdm(range(params.poll_interval), desc="sleeping between polls", ncols=100):
                time.sleep(1)
            print()
        else:
            time.sleep(params.poll_interval)


if __name__ == "__main__":
    main()
