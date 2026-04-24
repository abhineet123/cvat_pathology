import numpy as np
import json
import torch

from cellpose import models as cellpose_models

from cell_seg_gui import CellSegGUI

# import debugpy
# debugpy.listen(5678)


def init_context(context):
    context.logger.info("Init context...  0%")
    model = CellPoseGUI()
    context.user_data.model = model
    context.logger.info(f"Init context on {model.device}...100%")


def handler(context, event):
    context.logger.info("call handler")
    data = event.body
    model: CellPoseGUI = context.user_data.model
    threshold = float(data.get("threshold", 0))
    roi = data.get("obj_bbox", None)

    if roi is not None:
        results = model.infer_with_roi(event, context, threshold, roi)
    else:
        results = model.infer(event, context, threshold)
    return context.Response(
        body=json.dumps(results), headers={}, content_type="application/json", status_code=200
    )


class CellPoseGUI(CellSegGUI):
    def __init__(self):

        CellSegGUI.__init__(self)

        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        pretrained_model = "cpsam"
        # pixel_size = 0.2632
        # cell_size = 200
        # self.diameter = cell_size / pixel_size
        self.predictor = cellpose_models.CellposeModel(
            device=self.device,
            pretrained_model=pretrained_model,
        )

    def get_instance_mask(self, image: np.ndarray, threshold: float):
        flow_threshold = 0
        tile_norm_blocksize = 0
        cellprob_threshold = -10 * threshold if threshold > 0 else -0.1

        self.context.logger.info(f"cellprob_threshold: {cellprob_threshold}")

        out = self.predictor.eval(
            image,
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
        # cellprob = flows[-1]

        return masks
