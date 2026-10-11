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

from cell_seg_cli import CellSegCLIBase


class StardistCLI(CellSegCLIBase):
    def __init__(self, **kwargs) -> None:
        CellSegCLIBase.__init__(self, name="stardist", **kwargs)
        self.predictor = StarDist2D.from_pretrained("2D_versatile_he")

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: PIL.Image.Image, return_raw=False
    ) -> list[models.LabeledShapeRequest]:

        if context.frame_name == "B16 [x=105984,y=30464,w=256,h=256].png":
            """
            this empty image causes weird internal failure:
            terminate called recursively
            terminate called recursively
            terminate called recursively
            terminate called recursively
            terminate called recursively
            terminate called recursively
            Aborted (core dumped)
            """

            results = []
            self.update_status(context, results)
            return results

        image_np = normalize(np.array(image))
        try:
            labeled_output, _ = self.predictor.predict_instances(image_np)
        except:
            results = []
        else:
            results = self.instance_mask_to_cells(
                labeled_output,
            )

        self.update_status(context, results)
        return results
