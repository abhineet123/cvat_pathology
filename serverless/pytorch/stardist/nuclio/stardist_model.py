import numpy as np
from skimage.measure import approximate_polygon, find_contours

import tensorflow as tf

physical_devices = tf.config.list_physical_devices("GPU")
for gpu_instance in physical_devices:
    tf.config.experimental.set_memory_growth(gpu_instance, True)

from stardist.models import StarDist2D
from csbdeep.utils import normalize


def to_contour(mask):
    # mask.shape
    contours = find_contours(mask)
    contour = contours[0]
    contour = np.flip(contour, axis=1)
    contour = approximate_polygon(contour, tolerance=2.5)

    return contour


def to_cvat_mask(box: list, mask):
    xtl, ytl, xbr, ybr = box
    flattened = mask[ytl : ybr + 1, xtl : xbr + 1].flat[:].tolist()

    flattened = list(map(int, flattened))
    flattened.extend([xtl, ytl, xbr, ybr])
    return flattened


class StardistModel:
    def __init__(self):
        self.predictor = StarDist2D.from_pretrained("2D_versatile_he")

    def infer(self, image, context, threshold):
        image_np = normalize(np.array(image))

        labeled_output, _ = self.predictor.predict_instances(image_np)

        cell_ids = np.unique(labeled_output)

        results = []

        # exclude cell_id 0
        n_cells = len(cell_ids) - 1

        for i, cell_id in enumerate(cell_ids):
            if cell_id == 0:
                continue
            cell_mask = labeled_output == cell_id
            ys, xs = np.nonzero(cell_mask)
            xmin, ymin, xmax, ymax = np.amin(xs), np.amin(ys), np.amax(xs), np.amax(ys)
            bbox = [int(xmin), int(ymin), int(xmax), int(ymax)]

            context.logger.info(f"{i} / {n_cells}: {bbox}")
            cell_mask_uint8 = cell_mask.astype(np.uint8) * 255
            cvat_mask = to_cvat_mask(bbox, cell_mask_uint8)
            contour = to_contour(cell_mask_uint8)

            result = {
                "confidence": str(1),
                "label": "nucleus",
                "type": "mask",
                "points": contour.ravel().tolist(),
                "mask": cvat_mask,
            }
            results.append(result)
        return results
