# from typing import List
# from tqdm import tqdm
import PIL.Image
import numpy as np


import os

# import ray
# import os

import torch
from torchvision import transforms as T
import torch.nn.functional as F


import sys

import cvat_sdk.models as models
import cvat_sdk.auto_annotation as cvataa

from cell_seg_utils import linux_path, instance_mask_to_cells, CellSegCLIBase


class CellvitCLI(CellSegCLIBase):
    def __init__(
        self, task_name, label_name, n_frames, model_type="sam", verbose=True, **kwargs
    ) -> None:
        CellSegCLIBase.__init__(self, task_name, label_name, n_frames, verbose, "CellVIT")

        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        cellvit_path = linux_path(os.path.expanduser("~"), "cellvit")
        sys.path.append(cellvit_path)

        from cellvit.inference.postprocessing_cupy import (
            DetectionCellPostProcessorCupy as DetectionCellPostProcessor,
        )

        # from cellvit_postprocessing import DetectionCellPostProcessor
        from cellvit.utils.tools import unflatten_dict

        # Resolution for inference. Defaults to 0.25.
        self.resolution = 0.25

        self.model_root = linux_path(cellvit_path, "pretrained")

        if model_type == "sam":
            self.model_path = "SAM/CellViT-SAM-H-x40-AMP.pth"
        elif model_type == "hipt":
            self.model_path = "HIPT-256/CellViT-256-x40-AMP.pth"
        elif model_type == "virchow":
            self.model_path = "Virchow/CellViT-Virchow-x40-AMP.pth"
        else:
            raise AssertionError(f"invalid model_type {model_type}")

        self.model_path = linux_path(self.model_root, self.model_path)
        assert os.path.exists(self.model_path), f"invalid model_path: {self.model_path}"

        print(f"Loading checkpoint: {self.model_path}")

        model_checkpoint = torch.load(self.model_path, map_location="cpu")

        self.model_type = model_checkpoint["arch"]
        self.run_conf = unflatten_dict(model_checkpoint["config"], ".")

        print(f"creating model: {self.model_type}")

        if self.model_type in ["CellViT"]:
            from cellvit.models.cell_segmentation.cellvit import CellViT

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
            from cellvit.models.cell_segmentation.cellvit_256 import CellViT256

            self.model = CellViT256(
                model256_path=None,
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
                regression_loss=self.run_conf["model"].get("regression_loss", False),
            )
        elif self.model_type in ["CellVirchow"]:
            from cellvit.models.cell_segmentation.cellvit_virchow import CellViTVirchow

            self.model = CellViTVirchow(
                model_virchow_path=None,
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
            )

        elif self.model_type in ["CellViTSAM"]:
            from cellvit.models.cell_segmentation.cellvit_sam import CellViTSAM

            self.model = CellViTSAM(
                model_path=None,
                num_nuclei_classes=self.run_conf["data"]["num_nuclei_classes"],
                num_tissue_classes=self.run_conf["data"]["num_tissue_classes"],
                vit_structure=self.run_conf["model"]["backbone"],
                regression_loss=self.run_conf["model"].get("regression_loss", False),
            )
        elif self.pretrained_model == "CellViTUNI":
            from cellvit.models.cell_segmentation.cellvit_uni import CellViTUNI

            model = CellViTUNI(
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

    def detect(
        self, context: cvataa.DetectionFunctionContext, image: PIL.Image.Image, return_raw=False
    ) -> list[models.LabeledShapeRequest]:

        image_np = np.array(image)
        # image_np = np.expand_dims(image_np, axis=0)

        # print("showing image...")
        # cv2.imshow("image_np", image_np)
        # k = cv2.waitKey(0)
        # if k == ord("n"):
        #     return []
        # elif k == 27:
        #     exit(0)

        with torch.no_grad():
            patches = self.inference_transforms(image_np)
            # patches = patches[None, :, :, :]
            patches = torch.unsqueeze(patches, 0)
            patches = patches.to(self.device)

            if self.mixed_precision:
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    predictions = self.model.forward(patches, retrieve_tokens=True)
            else:
                predictions = self.model.forward(patches, retrieve_tokens=True)
            predictions = self.apply_softmax_reorder(predictions)

        instance_predictions, cell_dicts = self.postprocessor.post_process_batch(predictions)

        instance_predictions_np = torch.squeeze(instance_predictions).cpu().numpy()

        # nuclei_binary_map = torch.squeeze(predictions["nuclei_binary_map"]).cpu().numpy()
        # nuclei_binary_mask = np.argmax(nuclei_binary_map, axis=2)

        # nuclei_type_map = torch.squeeze(predictions["nuclei_type_map"]).cpu().numpy()
        # nuclei_type_mask = np.argmax(nuclei_type_map, axis=2)

        results = instance_mask_to_cells(instance_predictions_np, return_raw)
        self.update_status(context, results)
        return results

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
