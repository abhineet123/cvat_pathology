# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import json
import os
import sys
import base64
from PIL import Image
import io

# import debugpy
# debugpy.listen(5678)


def init_context(context):
    dirs = os.listdir()
    dirs_str = "\n".join(dirs)
    cwd = os.getcwd()

    sys.path.append(cwd)

    context.logger.info(f"cwd: {cwd}")
    context.logger.info(f"dirs:\n{dirs_str}")

    from cellvit_model import CellVITModel

    context.logger.info("Init context...  0%")
    model = CellVITModel()
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
