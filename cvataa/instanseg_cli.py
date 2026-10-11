from typing import List
from tqdm import tqdm
import PIL.Image
import torch
import numpy as np


from instanseg import InstanSeg

from cvat_sdk import make_client
import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa

from cell_seg_cli import CellSegCLIBase


class InstansegCLI(CellSegCLIBase):
    def __init__(self, **kwargs) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        CellSegCLIBase.__init__(self, name="instanseg", **kwargs)
        self.predictor = InstanSeg("brightfield_nuclei", verbosity=0, device=self.device)

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: PIL.Image.Image, return_raw=False
    ) -> list[models.LabeledShapeRequest]:
        pixel_size = 0.2632
        labeled_output = self.predictor.eval_small_image(
            np.array(image), pixel_size, return_image_tensor=False
        )

        labeled_output_np = labeled_output.cpu().detach().numpy().squeeze().astype(np.int64)
        results = self.instance_mask_to_cells(
            labeled_output_np,
        )
        self.update_status(context, results)
        return results
