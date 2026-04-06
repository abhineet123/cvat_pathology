# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import json
import base64
from PIL import Image
import io
from stardist_model import StardistModel

# import debugpy
# debugpy.listen(5678)


def init_context(context):
    context.logger.info("Init context...  0%")
    model = StardistModel()
    context.user_data.model = model
    context.logger.info("Init context...100%")


def handler(context, event):
    context.logger.info("call handler")
    data = event.body
    buf = io.BytesIO(base64.b64decode(data["image"]))
    image = Image.open(buf)
    threshold = float(data.get("threshold", 0))

    results = context.user_data.model.infer(image, context, threshold)

    return context.Response(
        body=json.dumps(results), headers={}, content_type="application/json", status_code=200
    )
