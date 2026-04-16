# from typing import List
# from tqdm import tqdm
import numpy as np

import cv2
import os
from PIL import Image

# import ray
# import os

import torch

# from torchvision import transforms as T
# import torch.nn.functional as F

import sys

import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa

from cell_seg_utils import instance_mask_to_cells, CellSegCLIBase, draw_box, linux_path

microsam_path = linux_path(os.path.expanduser("~"), "microsam")
sys.path.append(microsam_path)

from micro_sam.prompt_based_segmentation import segment_from_box
import micro_sam.util as util


class MicroSAMCLI(CellSegCLIBase):
    def __init__(
        self,
        task_name,
        n_frames,
        frame_name_to_shapes,
        model_type="vit_h_histopathology",
        verbose=True,
        **kwargs,
    ) -> None:
        CellSegCLIBase.__init__(self, task_name, n_frames, verbose, "MicroSAM")

        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.frame_name_to_shapes = frame_name_to_shapes

        """
        vit_l_lm: Model for cells and nuclei in light microscopy data with ViT Large image encoder. (idealistic-rat on BioImage.IO)
        vit_b_lm: Model for cells and nuclei in light microscopy data with ViT Base image encoder. (diplomatic-bug on BioImage.IO)
        vit_t_lm: Model for cells and nuclei in light microscopy data with ViT Tiny image encoder. (faithful-chicken BioImage.IO)

        vit_h_histopathology: Model for nuclei in histopathology with ViT Huge image encoder.
        vit_l_histopathology: Model for nuclei in histopathology with ViT Large image encoder.
        vit_b_histopathology: Model for nuclei in histopathology with ViT Base image encoder.

        """
        self.model_type = model_type
        print(f"creating MicroSAM model: {self.model_type}")

        self.predictor = util.get_sam_model(model_type=self.model_type, device=self.device)

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: Image.Image, return_raw=False
    ) -> list[models.LabeledShapeRequest]:

        frame_shapes = self.frame_name_to_shapes[context.frame_name]

        frame_shapes = [
            frame_shape for frame_shape in frame_shapes if frame_shape["type"] == "rectangle"
        ]

        image_np = np.array(image)

        # image_pil = Image.fromarray(image_np)
        # image_pil.show()

        cv2.imshow("image_np", image_np)
        cv2.waitKey(0)

        results = []
        if frame_shapes:
            img_h, img_w = image_np.shape[:2]
            instance_mask = np.zeros((img_h, img_w), dtype=np.int32)
            with torch.no_grad():
                self.predictor.reset_image()
                self.predictor.set_image(util._to_image(image_np))
                features = self.predictor.get_image_embedding().cpu().numpy()
                original_size = self.predictor.original_size
                input_size = self.predictor.input_size
                image_embeddings = {
                    "features": features,
                    "input_size": input_size,
                    "original_size": original_size,
                }
                # image_embeddings = util.precompute_image_embeddings(
                #     self.predictor, image_np, tile_shape=None, halo=None
                # )
                for frame_shape_id, frame_shape in enumerate(frame_shapes):
                    x1, y1, x2, y2 = frame_shape["points"]
                    bbox = np.asarray([y1, x1, y2, x2])

                    img_mask = segment_from_box(self.predictor, bbox, image_embeddings)
                    img_mask = img_mask.squeeze()

                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    img_mask_vis = img_mask.astype(np.uint8) * 255
                    draw_box(
                        img_mask_vis,
                        [x1, y1, x2, y2],
                        xywh=False,
                        thickness=2,
                        color=(255, 255, 255),
                    )
                    cv2.imshow("img_mask_vis", img_mask_vis)
                    k = cv2.waitKey(0)
                    if k == 27:
                        exit()

                    # bbox_mask = img_mask[y1:y1, x1:x2]

                    instance_mask[img_mask] = frame_shape_id + 1
                    print()
            results = instance_mask_to_cells(instance_mask, return_raw)

        self.update_status(context, results)

        return results
