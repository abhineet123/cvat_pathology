import json
import base64
from PIL import Image
import io
import numpy as np

import tensorflow as tf

physical_devices = tf.config.list_physical_devices("GPU")
for gpu_instance in physical_devices:
    tf.config.experimental.set_memory_growth(gpu_instance, True)

from stardist.models import StarDist2D
from csbdeep.utils import normalize

from cell_seg_gui import CellSegGUI

# import debugpy
# debugpy.listen(5678)


def init_context(context):
    context.logger.info("Init context...  0%")
    model = StardistGUI()
    context.user_data.model = model
    context.logger.info("Init context...100%")


def handler(context, event):
    context.logger.info("call handler")
    data = event.body
    model: StardistGUI = context.user_data.model
    threshold = float(data.get("threshold", 0))
    roi = data.get("obj_bbox", None)

    if roi is not None:
        results = model.infer_with_roi(event, context, threshold, roi)
    else:
        results = model.infer(event, context, threshold)
    return context.Response(
        body=json.dumps(results), headers={}, content_type="application/json", status_code=200
    )


class StardistGUI(CellSegGUI):
    def __init__(self):
        CellSegGUI.__init__(self)
        self.predictor = StarDist2D.from_pretrained("2D_versatile_he")

    def get_instance_mask(self, image, threshold):
        image_np = normalize(np.array(image))

        labeled_output, _ = self.predictor.predict_instances(image_np)

        return labeled_output
