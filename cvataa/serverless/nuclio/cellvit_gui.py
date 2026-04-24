import json
import os
import sys
import base64
from PIL import Image
import io

import numpy as np
import os

import urllib.request


import torch
from torchvision import transforms as T
import torch.nn.functional as F

from cellvit.models.cell_segmentation.cellvit import CellViT
from cellvit.models.cell_segmentation.cellvit_256 import CellViT256
from cellvit.models.cell_segmentation.cellvit_sam import CellViTSAM
from cellvit.models.cell_segmentation.cellvit_virchow import CellViTVirchow
from cellvit.models.cell_segmentation.cellvit_uni import CellViTUNI

from cellvit.inference.postprocessing_cupy import (
    DetectionCellPostProcessorCupy as DetectionCellPostProcessor,
)
from cellvit.utils.tools import unflatten_dict

from cell_seg_gui import CellSegGUI

# import debugpy
# debugpy.listen(5678)


def init_context(context):
    # dirs = os.listdir()
    # dirs_str = "\n".join(dirs)
    cwd = os.getcwd()
    sys.path.append(cwd)

    # context.logger.info(f"cwd: {cwd}")
    # context.logger.info(f"dirs:\n{dirs_str}")

    context.logger.info("Init context...  0%")
    model = CellVITGUI(context)
    context.user_data.model = model

    context.logger.info("Init context...100%")


def handler(context, event):
    context.logger.info("call handler")
    data = event.body
    model: CellVITGUI = context.user_data.model
    threshold = float(data.get("threshold", 0))
    roi = data.get("obj_bbox", None)

    if roi is not None:
        results = model.infer_with_roi(event, context, threshold, roi)
    else:
        results = model.infer(event, context, threshold)
    return context.Response(
        body=json.dumps(results), headers={}, content_type="application/json", status_code=200
    )


class CellVITGUI(CellSegGUI):
    def __init__(self, context):
        CellSegGUI.__init__(self)
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.resolution = 0.25

        self.model_url_root = "https://huggingface.co/abhineet123/cellvit_pp/resolve/main"
        try:
            model_type = os.environ["CELLVIT_VARIANT"]
        except KeyError:
            model_type = "sam"

        if model_type == "sam":
            self.ckpt = "CellViT-SAM-H-x40-AMP.pth"
        elif model_type == "hipt":
            self.ckpt = "CellViT-256-x40-AMP.pth"
        elif model_type == "virchow":
            self.ckpt = "CellViT-Virchow-x40-AMP.pth"
        else:
            raise AssertionError(f"invalid model_type {model_type}")

        if not os.path.exists(self.ckpt):
            self.model_url = f"{self.model_url_root}/{self.ckpt}"
            context.logger.info(f"downloading ckpt: {self.model_url}")

            urllib.request.urlretrieve(f"{self.model_url}", f"{self.ckpt}")

        assert os.path.exists(self.ckpt), f"ckpt not found: {self.ckpt}"

        context.logger.info(f"Loading checkpoint: {self.ckpt}")

        model_checkpoint = torch.load(self.ckpt, map_location="cpu")

        self.model_type = model_checkpoint["arch"]
        self.run_conf = unflatten_dict(model_checkpoint["config"], ".")

        context.logger.info(f"creating model: {self.model_type}")

        if self.model_type in ["CellViT"]:
            self.model = CellViT(
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
                embed_dim=self.run_conf["model"]["embed_dim"],
                input_channels=self.run_conf["model"].get("input_channels", 3),
                depth=self.run_conf["model"]["depth"],
                num_heads=self.run_conf["model"]["num_heads"],
                extract_layers=self.run_conf["model"]["extract_layers"],
                regression_loss=self.run_conf["model"].get("regression_loss", False),
            )
        elif self.model_type in ["CellViT256"]:
            self.model = CellViT256(
                model256_path=None,
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
                regression_loss=self.run_conf["model"].get("regression_loss", False),
            )
        elif self.model_type in ["CellViTVirchow"]:
            self.model = CellViTVirchow(
                model_virchow_path=None,
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
            )

        elif self.model_type in ["CellViTSAM"]:
            self.model = CellViTSAM(
                model_path=None,
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
                vit_structure=self.run_conf["model"]["backbone"],
                regression_loss=self.run_conf["model"].get("regression_loss", False),
            )
        elif self.model_type in ["CellViTUNI"]:
            self.model = CellViTUNI(
                model_uni_path=None,
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
            )
        else:
            raise AssertionError(f"invalid pretrained_model: {self.model_type}")

        self.model.load_state_dict(model_checkpoint["model_state_dict"])
        self.model.eval()
        self.model.to(self.device)
        self.postprocessor = DetectionCellPostProcessor(
            wsi=None,
            nr_types=self.run_conf["data"]["num_nuclei_classes"],
            binary=False,
        )

        self.run_conf["model"]["token_patch_size"] = self.model.patch_size
        self.model_arch = model_checkpoint["arch"]

        print(f"loading inference transforms")

        self._load_inference_transforms()
        self._setup_amp(enforce_mixed_precision=False)
        # self._setup_worker()

        self.binary = True

        self.batch_size = 1

    def _load_inference_transforms(self):
        """Load the inference transformations from the run_configuration"""

        transform_settings = self.run_conf["transformations"]
        if "normalize" in transform_settings:
            mean = transform_settings["normalize"].get("mean", (0.5, 0.5, 0.5))
            std = transform_settings["normalize"].get("std", (0.5, 0.5, 0.5))
        else:
            mean = (0.5, 0.5, 0.5)
            std = (0.5, 0.5, 0.5)
        self.inference_transforms = T.Compose([T.ToTensor(), T.Normalize(mean=mean, std=std)])

    def _setup_amp(self, enforce_mixed_precision: bool = False) -> None:
        """Setup automated mixed precision (amp) for inference.

        Args:
            enforce_mixed_precision (bool, optional): Using PyTorch autocasting with dtype float16 to speed up inference. Also good for trained amp networks.
                Can be used to enforce amp inference even for networks trained without amp. Otherwise, the network setting is used.
                Defaults to False.
        """
        if enforce_mixed_precision:
            self.mixed_precision = enforce_mixed_precision
        else:
            self.mixed_precision = self.run_conf["training"].get("mixed_precision", False)

    def apply_softmax_reorder(self, predictions: dict) -> dict:
        """Reorder and apply softmax on predictions

        Args:
            predictions(dict): Predictions

        Returns:
            dict: Predictions
        """
        predictions["nuclei_binary_map"] = F.softmax(predictions["nuclei_binary_map"], dim=1)
        predictions["nuclei_type_map"] = F.softmax(predictions["nuclei_type_map"], dim=1)
        predictions["nuclei_type_map"] = predictions["nuclei_type_map"].permute(0, 2, 3, 1)
        predictions["nuclei_binary_map"] = predictions["nuclei_binary_map"].permute(0, 2, 3, 1)
        predictions["hv_map"] = predictions["hv_map"].permute(0, 2, 3, 1)
        return predictions

    def get_instance_mask(self, image, threshold):

        self.context.logger.info(f"threshold: {threshold}")

        # image = np.expand_dims(image, axis=0)

        with torch.no_grad():
            patches = self.inference_transforms(image)
            # patches = patches[None, :, :, :]
            patches = torch.unsqueeze(patches, 0)
            patches = patches.to(self.device)

            if self.mixed_precision:
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    predictions = self.model.forward(patches, retrieve_tokens=True)
            else:
                predictions = self.model.forward(patches, retrieve_tokens=True)
            predictions = self.apply_softmax_reorder(predictions)

        instance_predictions, cell_dicts = self.postprocessor.post_process_batch(
            predictions, threshold=threshold
        )

        instance_predictions_np = torch.squeeze(instance_predictions).cpu().numpy()

        return instance_predictions_np
