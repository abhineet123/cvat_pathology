import numpy as np
import json
import torch

from instanseg import InstanSeg

from cell_seg_gui import CellSegGUI

# import debugpy
# debugpy.listen(5678)


def init_context(context):
    context.logger.info("Init context...  0%")
    model = InstansegGUI()
    context.user_data.model = model
    context.logger.info(f"Init context on {model.device}...100%")


def handler(context, event):
    context.logger.info("call handler")
    data = event.body
    model: InstansegGUI = context.user_data.model
    threshold = float(data.get("threshold", 0))
    roi = data.get("obj_bbox", None)

    if roi is not None:
        results = model.infer_with_roi(event, context, threshold, roi)
    else:
        results = model.infer(event, context, threshold)
    return context.Response(
        body=json.dumps(results), headers={}, content_type="application/json", status_code=200
    )


class InstansegGUI(CellSegGUI):
    def __init__(self):
        CellSegGUI.__init__(self)

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.latest_image = None
        self.predictor = InstanSeg("brightfield_nuclei", verbosity=0, device=self.device)

    def get_instance_mask(self, image, threshold):
        pixel_size = None
        labeled_output = self.predictor.eval_small_image(
            image, pixel_size, return_image_tensor=False
        )

        labeled_output_np = labeled_output.cpu().detach().numpy().squeeze().astype(np.int32)

        return labeled_output_np
