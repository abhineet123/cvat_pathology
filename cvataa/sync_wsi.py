from tqdm import tqdm
import os
import time

from datetime import datetime
from pathlib import Path
import json
import subprocess

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
        self.enable = 0
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
        self.ann_ext = ".geojson.gz"

        self.qupath_suffix = "QP"
        self.annotations_dir = "annotations"

        self.qp_exe = "QuPath"
        self.qp_dir = "qupath"
        self.qp_script = "create_project_headless.groovy"

        self.start_time = 00
        self.end_time = 24
        self.verbose = 0

        self.poll_interval = 10
        self.fin_wait_t = 10
        self.max_days = 30
        self.time_fmt = "%y%m%d_%H%M%S"
        self.date_fmt = "%Y_%m_%d"


def copy_dir_with_rsync(src, dst, exclusion=None):
    cmds = [
        "rsync",
        "-a",
    ]
    if exclusion is not None:
        cmds += ["--exclude", exclusion]
    cmds += [src, dst]

    subprocess.call(cmds)


def copy_file_with_rsync(src, dst):
    subprocess.call(["rsync", "--info=progress2", src, dst])


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


def sync_file(params: Params, files_info: dict, shared_path: str, logger, orig_name=None):

    shared_name = utils.path_to_name(shared_path, remove_ext=False)
    if shared_name in files_info:
        file_dict = files_info[shared_name]
        if is_previously_copied(file_dict, shared_path, params.time_fmt):
            return False
    else:
        file_dict = dict()

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

    files_info[shared_name] = file_dict
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


def get_patient_info(patient_dir, day_dir, wsi_log, time_fmt):
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
            day=day_dir.name,
            timestamp=timestamp,
            accession_id=accession_id,
            wsi={},
            annotations={},
        )

    return patient_dict


def rename_file(params: Params, patient_dir, src_name, dst_name):
    print(f"renaming {src_name} >> {dst_name}")

    src_path = utils.linux_path(patient_dir, src_name)
    dst_path = utils.linux_path(patient_dir, dst_name)

    utils.wait_for_file_to_finalize(src_path, params.fin_wait_t, params.verbose)

    os.rename(src_path, dst_path)

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

    barcodes, scan_times = zip(*[f.name.split("_") for f in patient_wsis])

    barcodes_sort_indices = sorted(range(len(barcodes)), key=lambda i: barcodes[i])
    scan_times_sort_indices = sorted(range(len(scan_times)), key=lambda i: scan_times[i])

    src_to_dst_names = {}
    dst_path_to_src_name = {}

    for file_id, assay in zip(scan_times_sort_indices, params.assays, strict=True):
        src_name = patient_wsis[file_id].name
        dst_name = f"{accession_id}-{assay}{params.wsi_ext}"

        dst_path = rename_file(params, patient_dir, src_name, dst_name)

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

    log_updated = False
    for dst_path, src_name in dst_path_to_src_name.items():
        if sync_file(params, patient_info["wsi"], dst_path, logger, src_name):
            log_updated = True

    if not os.path.isdir(qp_proj_path):
        print(f"Creating QuPath project: {qp_proj_path}")
        os.makedirs(qp_proj_path)
        if params.qp_exe:
            assert params.qp_script, "qupath_script must be provided"
            script_dir_path = str(Path(__file__).resolve().parent)
            groovy_script_path = utils.linux_path(script_dir_path, params.qp_dir, params.qp_script)
            assert os.path.isfile(
                groovy_script_path
            ), f"invalid groovy script: {groovy_script_path}"
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

            logger.info(f"running qupath cmd: {qp_cmds}")
            subprocess.call(qp_cmds)

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

    while True:
        if params.verbose:
            print()

        day_dirs = [
            f
            for f in os.scandir(params.shared_root)
            if f.is_dir() and not f.name.startswith(".") and utils.is_date(f.name, params.date_fmt)
        ]
        day_dirs.sort(key=utils.path_to_name, reverse=True)
        n_days = len(day_dirs)
        if n_days > params.max_days > 0:
            day_dirs = day_dirs[: params.max_days]
            n_days = len(day_dirs)

        patients_dirs = [
            (p, d, get_patient_info(p, d, json_log, params.time_fmt))
            for d in day_dirs
            for p in os.scandir(d.path)
            if p.is_dir()
        ]
        log_updated = False

        if params.verbose:
            pbar = tqdm(patients_dirs, desc="polling for change", ncols=100)
        else:
            pbar = patients_dirs

        for patient_dir, day_dir, patient_info in pbar:
            accession_id = patient_info["accession_id"]

            qp_proj_path = utils.linux_path(
                patient_dir.path, f"{accession_id}-{params.qupath_suffix}"
            )

            log_updated = process_wsi_files_v2(
                params, patient_info, patient_dir, accession_id, qp_proj_path, logger
            )

            ann_dir_path = utils.linux_path(qp_proj_path, params.annotations_dir)
            if not os.path.isdir(ann_dir_path):
                continue

            ann_paths = [
                utils.linux_path(ann_dir_path, f"{accession_id}-{assay_type}{params.ann_ext}")
                for assay_type in params.assays
            ]
            patient_anns = [ann_path for ann_path in ann_paths if os.path.exists(ann_path)]

            for ann in patient_anns:
                if sync_file(params, patient_info["annotations"], ann, logger):
                    sync_dir(params, qp_proj_path, exclusion=params.annotations_dir)
                    log_updated = True

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
