import PIL.Image
import numpy as np

import tensorflow as tf

physical_devices = tf.config.list_physical_devices("GPU")
for gpu_instance in physical_devices:
    tf.config.experimental.set_memory_growth(gpu_instance, True)

from stardist.models import StarDist2D

from cvat_sdk import make_client
import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa
from csbdeep.utils import normalize

from cell_seg_utils import instance_mask_to_cells, CellSegCLIBase


class StardistCLI(CellSegCLIBase):
    def __init__(self, task_name, n_frames, verbose=True, **kwargs) -> None:
        CellSegCLIBase.__init__(self, task_name, n_frames, verbose, "StarDist")
        self.predictor = StarDist2D.from_pretrained("2D_versatile_he")

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: PIL.Image.Image, return_raw=False
    ) -> list[models.LabeledShapeRequest]:
        image_np = normalize(np.array(image))
        labeled_output, _ = self.predictor.predict_instances(image_np)

        results = instance_mask_to_cells(labeled_output, return_raw)

        self.update_status(context, results)
        return results
