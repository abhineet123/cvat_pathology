from typing import List
from tqdm import tqdm
import PIL.Image
import torch
import numpy as np

from cellpose import models as cellpose_models
from cellpose import transforms as cellpose_transforms

from cvat_sdk import make_client
import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa

from cell_seg_cli import CellSegCLIBase


class CellposeCLI(CellSegCLIBase):
    def __init__(self, **kwargs) -> None:
        CellSegCLIBase.__init__(
            self,
            name="cellpose",
            **kwargs,
        )

        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        pretrained_model = "cpsam"
        pixel_size = 0.2632
        cell_size = 200
        self.diameter = cell_size / pixel_size
        self.predictor = cellpose_models.CellposeModel(
            device=self.device,
            pretrained_model=pretrained_model,
        )

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: PIL.Image.Image
    ) -> list[models.LabeledShapeRequest]:
        image_np = np.array(image)

        # image_h, image_w = image_np.shape[:2]
        # image_np_t = image_np.transpose((2, 0, 1))

        # image_transformed = cellpose_transforms.convert_image(image_np_t, do_3D=False)
        image_transformed = image_np

        flow_threshold = 0
        cellprob_threshold = -1
        tile_norm_blocksize = 0

        out = self.predictor.eval(
            image_transformed,
            niter=1000,
            # diameter=self.diameter,
            diameter=None,
            normalize={"tile_norm_blocksize": tile_norm_blocksize},
            do_3D=False,
            augment=False,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
            stitch_threshold=0.0,
            min_size=-1,
            batch_size=64,
            bsize=256,
            resample=True,
            channel_axis=None,
            z_axis=None,
            flow3D_smooth=0,
        )
        masks, flows = out[:2]
        cellprob = flows[-1]

        results = self.instance_mask_to_cells(
            masks,
        )
        self.update_status(context, results)
        return results
