# Copyright (C) CVAT.ai Corporation
#
# SPDX-License-Identifier: MIT

import json
from cellpose_model import CellPoseModel

# import debugpy
# debugpy.listen(5678)


def init_context(context):
    context.logger.info("Init context...  0%")
    model = CellPoseModel()
    context.user_data.model = model
    context.logger.info(f"Init context on {model.device}...100%")


def handler(context, event):
    context.logger.info("call handler")
    data = event.body
    roi = data.get("obj_bbox", None)
    threshold = float(data.get("threshold", 0))

    if roi is not None:
        pos_points = data.get("pos_points", None)
        results = context.user_data.model.infer_with_roi(event, context, threshold, roi, pos_points)
    else:
        results = context.user_data.model.infer(event, context, threshold)

    return context.Response(
        body=json.dumps(results), headers={}, content_type="application/json", status_code=200
    )
