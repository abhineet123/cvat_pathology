import os
import itertools

from PIL import Image
import numpy as np

import cvat_sdk.auto_annotation as cvataa
import cvat_sdk.models as models

from cell_seg_cli import CellSegCLIBase

from cell_seg_utils import (
    mask_rgb_to_id,
)


class LoadAnnotations(CellSegCLIBase):
    def __init__(
        self, load_dir, task_name, client, task_name_to_obj, label_name, n_frames, verbose=True
    ) -> None:
        CellSegCLIBase.__init__(
            self,
            task_name,
            client,
            task_name_to_obj,
            label_name,
            n_frames,
            verbose,
            "LoadAnnotations",
        )
        self.load_dir = load_dir
        image_exts = ["bmp", "png", "tif"]
        self.mask_paths = [
            os.path.join(self.load_dir, k)
            for k in os.listdir(self.load_dir)
            if any(k.lower().endswith(f".{_ext}") for _ext in image_exts)
        ]
        self.mask_name_to_path = {
            os.path.splitext(os.path.basename(mask_path))[0]: mask_path
            for mask_path in self.mask_paths
        }
        all_rgb_cols = list(itertools.product(range(256), repeat=3))
        self.rgb_cols_to_id = {rgb_col: i for i, rgb_col in enumerate(all_rgb_cols) if i > 0}

        print(f"loading annotations from {self.load_dir}")

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: Image.Image, return_raw=False
    ) -> list[models.LabeledShapeRequest]:

        frame_name = os.path.splitext(os.path.basename(context.frame_name))[0]

        try:
            mask_path = self.mask_name_to_path[frame_name]
        except KeyError:
            print(f"using empty mask for nonexistent frame: {frame_name} ")
            results = []
        else:
            mask_rgb = np.asarray(Image.open(mask_path))
            mask_id = mask_rgb_to_id(mask_rgb, self.rgb_cols_to_id)
            results = self.instance_mask_to_cells(
                mask_id,
                return_raw,
                model="cellpose",
                label_id=self.label_id,
                attribute_name_to_id=self.attribute_name_to_id,
            )
            results = self.iinstance_mask_to_cells(mask_id, return_raw)

        self.update_status(context, results)
        return results
