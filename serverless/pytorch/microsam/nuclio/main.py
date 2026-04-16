import json
import base64
from PIL import Image
import io
from microsam_model import MicroSAMModel

import debugpy

debugpy.listen(5679)


def init_context(context):
    context.logger.info("Init context...  0%")
    model = MicroSAMModel(context)
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
