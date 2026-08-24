import os
import numpy as np
from collections import defaultdict

import paramparse
from tqdm import tqdm
import pandas as pd

import fiftyone as fo
import compress_json

import cell_seg_utils as utils


class Params(paramparse.CFG):
    def __init__(self):
        paramparse.CFG.__init__(self, cfg_prefix="vw")

        self.filter = utils.Filter()

        self.eval_dir = "lists/eval"
        self.eval_file = ""
        self.eval_ext = ".xlsx"

        self.out_dir = ""

        self.max_samples = 0

        self.start_id = 0
        self.end_id = -1

        self.model = "cellpose"
        self.search = ""


def url_to_dataset_name(url):
    # url_parts = list(urllib.parse.urlsplit(url))
    url_parts = url.split("/")
    db_name_id = url_parts.index("datasets") + 1
    db_name = url_parts[db_name_id]
    if "?" in db_name:
        db_name = db_name.split("?")[0]
    return db_name


def get_datasets(filter: utils.Filter, allow_empty=True):
    dataset_names = list(fo.list_datasets())
    dataset_names = filter.apply(dataset_names)
    dataset_names.sort()
    if not allow_empty:
        assert dataset_names, "no valid datasets found"

    return dataset_names


def main():
    params: Params = paramparse.process(Params)

    if not params.eval_file:
        assert params.search, "search term must be provided in lieu of eval_file"
        all_datasets = get_datasets(params.filter, allow_empty=True)
        for dataset_name in tqdm(all_datasets):
            dataset = fo.load_dataset(dataset_name)
            pbar = tqdm(
                dataset.iter_groups(),
                total=len(dataset),
            )
            for tile_id, tile_group in enumerate(pbar):
                for model, sample in tile_group.items():
                    if sample.id.startswith(params.search):
                        print(f"found search term in dataset {dataset_name}")
                        exit(0)
                    print(f"{dataset_name} {model} {sample.id}")
                break
            print(f"\n")
        return

    assert params.model, "model must be provided"

    if not params.eval_file.endswith(params.eval_ext):
        params.eval_file = f"{params.eval_file}{params.eval_ext}"

    eval_file_path = utils.linux_path(params.eval_dir, params.eval_file)

    df = pd.read_excel(eval_file_path)

    n_rows = df.shape[0]

    wsi_to_all = defaultdict(list)
    wsi_to_fail = defaultdict(list)
    wsi_to_pass = defaultdict(list)

    for index, row in df.iterrows():

        if index < params.start_id > 0:
            print(f"skipping rows before {params.start_id}")
            continue

        if index > params.end_id >= 0:
            print(f"skipping rows beyond {params.end_id}")
            break

        url = row["URL"]
        tiles = row["Tiles"]
        examined = row["Examined"]

        try:
            fail_ids = tiles.split(",")
        except AttributeError:
            fail_ids = []
        else:
            fail_ids_unique = list(set(fail_ids))
            assert len(fail_ids) == len(fail_ids_unique), "duplicate fail_ids found"

        dataset_name = url_to_dataset_name(url)
        dataset = fo.load_dataset(dataset_name)

        n_samples = len(dataset)

        total_fails = len(fail_ids)

        if examined > 0:
            assert n_samples >= examined, "examined count exceeeds n_samples"
            print(f"examined count: {examined} / {n_samples}")
        else:
            examined = n_samples

        tile_id = 0

        fail_ids_found = []

        n_fail = n_pass = 0

        fail_id_to_info = {}
        fail_ids_not_found = fail_ids[:]

        """some of the fail IDs can be from other models so go through all models to find them"""
        pbar = tqdm(
            dataset.iter_groups(),
            total=examined,
        )

        for tile_id, tile_group in enumerate(pbar):
            if tile_id >= examined > 0:
                print(f"skipping unexamined samples beyond {examined}")
                break

            if tile_id >= params.max_samples > 0:
                print(f"skipping samples beyond {params.max_samples}")
                break

            tile_path = tile_group[params.model].filepath
            wsi_name = os.path.basename(os.path.dirname(tile_path))

            wsi_to_all[wsi_name].append(tile_path)

            """some of the fail IDs can be from other models so go through all models to find them"""
            for model, sample in tile_group.items():

                assert (
                    tile_path == sample.filepath
                ), f"{model} sample filepath does not match tile_path"

                if sample.id not in fail_ids_not_found:
                    continue

                fail_ids_found.append(sample.id)
                fail_ids_not_found.remove(sample.id)
                fail_id_to_info[sample.id] = f"{tile_id} {model} {tile_path}"

                wsi_to_fail[wsi_name].append(tile_path)
                n_fail += 1
                break
            else:
                """none of the models for this tile have a sample id that is marked as fail so this tile is a pass"""
                wsi_to_pass[wsi_name].append(tile_path)
                n_pass += 1

                pbar.set_description(
                    f"{index+1}/{n_rows} {dataset_name} (f: {n_fail}/{total_fails} p: {n_pass})"
                )

        if fail_ids_not_found:
            n_fail_ids_not_found = len(fail_ids_not_found)
            print(
                f"{n_fail_ids_not_found} fail id(s) not found:\n{utils.to_str(fail_ids_not_found)}"
            )
            assert (
                examined < n_samples
            ), f"entire dataset has already been examined so there are no out-of-range samples to search for the missing fail id(s)"

            if fail_ids_found:
                fail_samples_found = [fail_id_to_info[fail_id] for fail_id in fail_ids_found]
                print(
                    f"\nfail_samples_found:\n{utils.to_str_multi((fail_ids_found, fail_samples_found))}\n"
                )

            pbar = tqdm(
                dataset.iter_groups(),
                total=n_samples,
            )
            n_fail = 0
            fail_samples_out_of_range = []
            fail_ids_not_valid = fail_ids_not_found[:]
            for tile_id, tile_group in enumerate(pbar):
                if tile_id < examined:
                    continue
                for model, sample in tile_group.items():
                    if sample.id in fail_ids_not_valid:
                        fail_samples_out_of_range.append(
                            f"{sample.id} {tile_id} {model} {sample.filepath}"
                        )
                        fail_ids_not_valid.remove(sample.id)
                        if not fail_ids_not_valid:
                            break
                        n_fail += 1
                pbar.set_description(f"(fail_id_to_info: {n_fail}/{n_fail_ids_not_found}")
                if not fail_ids_not_valid:
                    break

            if fail_samples_out_of_range:
                print(f"\nfail_samples_not_found:\n{utils.to_str(fail_samples_out_of_range)}\n")

            raise AssertionError()

    if not params.out_dir:
        eval_name = utils.path_to_name(eval_file_path)
        params.out_dir = utils.linux_path(params.eval_dir, eval_name)

    print(f"saving output json files to {params.out_dir}")

    os.makedirs(params.out_dir, exist_ok=True)

    json_kwargs = dict(indent=4)

    compress_json.dump(
        wsi_to_fail,
        utils.linux_path(params.out_dir, f"fail.json.gz"),
        json_kwargs=json_kwargs,
    )
    compress_json.dump(
        wsi_to_pass,
        utils.linux_path(params.out_dir, f"pass.json.gz"),
        json_kwargs=json_kwargs,
    )
    compress_json.dump(
        wsi_to_all,
        utils.linux_path(params.out_dir, f"all.json.gz"),
        json_kwargs=json_kwargs,
    )


if __name__ == "__main__":
    main()
