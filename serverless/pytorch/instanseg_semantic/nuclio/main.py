# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import json
import base64
from PIL import Image
import io
from model_handler import ModelHandler

# import debugpy
# debugpy.listen(5678)

def init_context(context):
    context.logger.info("Init context...  0%")
    model = ModelHandler()
    context.user_data.model = model
    context.logger.info("Init context...100%")
    context.logger.info(f"Init context on {model.device}...100%")


def handler(context, event):
    context.logger.info("call handler")
    data = event.body
    buf = io.BytesIO(base64.b64decode(data["image"]))
    image = Image.open(buf)
    output_type = int(data.get("threshold", 0))

    results = context.user_data.model.infer(image, context, output_type)

    return context.Response(
        body=json.dumps(results), headers={}, content_type="application/json", status_code=200
    )

