import PIL.Image
import numpy as np

import tensorflow as tf

physical_devices = tf.config.list_physical_devices("GPU")
for gpu_instance in physical_devices:
    tf.config.experimental.set_memory_growth(gpu_instance, True)

from csbdeep.utils import normalize

from cell_seg_params import StarDistParams


from cell_seg_wsi import CellSegWSIBase


class StardistWSI(CellSegWSIBase):
    def __init__(self, params: StarDistParams, file_mode):
        CellSegWSIBase.__init__(
            self,
            name="stardist",
            file_mode=file_mode,
            params=params,
        )
        from stardist.models import StarDist2D

        self.predictor = StarDist2D.from_pretrained("2D_versatile_he")

    def detect_in_file(self, wsi_path, mask_path, ann_path, outdir):
        assert outdir, "outdir must be provided"

        raise NotImplementedError("stardist detect_in_file is not implemented")

    def detect(self, wsi):
        self.frame_id += 1
        wsi_np = normalize(np.array(wsi))
        labels, _ = self.predictor.predict_instances(normalize(wsi_np))

        try:
            labeled_output, _ = self.predictor.predict_instances(wsi_np)
        except:
            results = []
        else:
            results = self.instance_mask_to_cells(
                labeled_output,
            )
        return results
