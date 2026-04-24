import json
import os
import numpy as np
import base64
import io

from PIL import Image

import torch


from micro_sam.prompt_based_segmentation import segment_from_box
import micro_sam.util as util

from cell_seg_gui import CellSegGUI


# import debugpy
# debugpy.listen(5679)


def init_context(context):
    context.logger.info("Init context...  0%")
    model = MicroSAMGUI(context)
    context.user_data.model = model
    context.logger.info("Init context...100%")


def handler(context, event):
    context.logger.info("microsam call handler")
    data = event.body
    # pos_points = data["pos_points"]
    # neg_points = data["neg_points"]
    obj_bbox = data.get("obj_bbox", None)

    if obj_bbox is None:
        return context.Response(
            body="",
            headers={},
            content_type="application/json",
            status_code=200,
        )

    buf = io.BytesIO(base64.b64decode(data["image"]))
    image = Image.open(buf)

    mask = context.user_data.model.handle(context, event, image, obj_bbox)
    return context.Response(
        body=json.dumps({"mask": mask.tolist()}),
        headers={},
        content_type="application/json",
        status_code=200,
    )


class MicroSAMGUI:
    def __init__(self, context):
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        self.model_type = os.environ.get("MICROSAM_VARIANT", "vit_t_lm")
        """
        vit_l_lm: Model for cells and nuclei in light microscopy data with ViT Large image encoder. (idealistic-rat on BioImage.IO)
        vit_b_lm: Model for cells and nuclei in light microscopy data with ViT Base image encoder. (diplomatic-bug on BioImage.IO)
        vit_t_lm: Model for cells and nuclei in light microscopy data with ViT Tiny image encoder. (faithful-chicken BioImage.IO)

        vit_h_histopathology: Model for nuclei in histopathology with ViT Huge image encoder.
        vit_l_histopathology: Model for nuclei in histopathology with ViT Large image encoder.
        vit_b_histopathology: Model for nuclei in histopathology with ViT Base image encoder.
        """
        context.logger.info(f"loading microsam model: {self.model_type}")

        self.predictor = util.get_sam_model(model_type=self.model_type, device=self.device)

        # self.contexts = []
        # self.events = []

        self.prev_image = None
        self.prev_embeddings = None

    def handle(
        self,
        context,
        event,
        image,
        bbox,
    ):
        # return

        # self.contexts.append(context)
        # self.events.append(event)

        image_np = np.array(image)
        bbox = list(np.squeeze(bbox))

        # context.logger.info(f"bbox: {bbox}")

        with torch.no_grad():
            image_bytes = event.body["image"]
            if image_bytes != self.prev_image:
                context.logger.info(f"computing embeddings for new image")
                self.prev_image = image_bytes
                self.predictor.reset_image()
                self.predictor.set_image(util._to_image(image_np))
                features = self.predictor.get_image_embedding().cpu().numpy()
                original_size = self.predictor.original_size
                input_size = self.predictor.input_size
                self.prev_embeddings = {
                    "features": features,
                    "input_size": input_size,
                    "original_size": original_size,
                }
            else:
                context.logger.info(f"reusing previously computed embeddings")

            x1, y1 = bbox[0]
            x2, y2 = bbox[1]

            box_yx = np.asarray([y1, x1, y2, x2])

            img_mask = segment_from_box(self.predictor, box_yx, self.prev_embeddings)

        img_mask = img_mask.squeeze().astype(np.uint8) * 255
        # cv2.normalize(img_mask, img_mask, 0, 255, cv2.NORM_MINMAX)
        # context.logger.info(f"img_mask: {img_mask}")
        return img_mask
