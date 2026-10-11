import PIL.Image
import numpy as np
from pathlib import Path
import os
import cv2

import torch
from torchvision import transforms as T
import torch.nn.functional as F

from einops import rearrange

import sys

from cell_seg_params import CellVITParams
from cell_seg_utils import linux_path
from cell_seg_wsi import CellSegWSIBase

cellvit_path = linux_path(os.path.expanduser("~"), "cellvit")
sys.path.append(cellvit_path)

from cellvit.utils.tools import unflatten_dict
from cellvit.inference.postprocessing_cupy import (
    DetectionCellPostProcessorCupy as DetectionCellPostProcessor,
)


class CellVITWSI(CellSegWSIBase):
    def __init__(self, params: CellVITParams, file_mode):
        CellSegWSIBase.__init__(
            self,
            name=f"cellvit-{params.model_type}",
            file_mode=file_mode,
            params=params,
        )
        self.params: CellVITParams = params
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        if self.params.classifier:
            self.name = f"{self.name}-{self.params.classifier}"

        self.model_root = linux_path(cellvit_path, "pretrained")
        self.classifier_root = linux_path(cellvit_path, "checkpoints", "classifier", "sam-h")

        if self.params.model_type == "sam":
            self.model_path = "SAM/CellViT-SAM-H-x40-AMP.pth"
        elif self.params.model_type == "hipt":
            self.model_path = "HIPT-256/CellViT-256-x40-AMP.pth"
        elif self.params.model_type == "virchow":
            self.model_path = "Virchow/CellViT-Virchow-x40-AMP.pth"
        else:
            raise AssertionError(f"invalid model_type {self.params.model_type}")

        self.model_path = linux_path(self.model_root, self.model_path)
        assert os.path.exists(self.model_path), f"invalid model_path: {self.model_path}"

        self.binary = self.params.binary

        self.classifier_path = (
            None
            if not self.params.classifier
            else linux_path(self.classifier_root, f"{self.params.classifier}.pth")
        )

        if self.file_mode:
            from cellvit.inference.inference_memory import CellViTInferenceMemory

            self.celldetector = CellViTInferenceMemory(
                model_path=self.model_path,
                classifier_path=self.classifier_path,
                binary=self.binary,
                gpu=self.params.gpu,
                outdir="",
                geojson=self.params.geojson,
                graph=self.params.graph,
                compression=self.params.compression,
                patch_size=self.params.patch_size,
                batch_size=self.params.batch_size,
                enforce_mixed_precision=self.params.mp,
                chunk_size=self.params.chunk_size,
            )
            return

        self._load_detector()
        self._load_classifier()

        self.postprocessor = DetectionCellPostProcessor(
            wsi=None,
            nr_types=self.run_conf["data"]["num_nuclei_classes"],
            classifier=self.classifier,
            binary=False,
        )
        self._load_inference_transforms()
        self.mp = self.params.mp or self.run_conf["training"].get("mixed_precision", False)

    def detect_in_file(self, wsi_path, mask_path, ann_path, outdir):

        assert outdir, "outdir must be provided"

        self.celldetector.outdir = Path(outdir)

        cell_dict_wsi = self.celldetector.process_wsi(
            wsi_path=Path(wsi_path),
            wsi_properties={},
            resolution=self.params.resolution,
            annotation_path=ann_path,
            label_map={"background": 0, "tissue": 1},
        )

        # wsi_metadata = cell_dict_wsi["wsi_metadata"]
        # wsi_type_map = cell_dict_wsi["type_map"]
        # wsi_cells = cell_dict_wsi["cells"]

        # print()

    def _load_detector(self) -> None:
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

        self.run_conf["model"]["token_patch_size"] = self.model.patch_size
        self.model_arch = model_checkpoint["arch"]

        self.label_map = self.run_conf["dataset_config"]["nuclei_types"]
        self.label_map = {int(v): k for k, v in self.label_map.items()}

    def _load_classifier(self) -> None:
        """Load the classifier if provided

        Args:
            classifier_path (Union[Path, str], optional): Path to classifier. Defaults to None.
        """
        from cellvit.models.classifier.linear_classifier import LinearClassifier

        if self.classifier_path is None:
            self.classifier = None
            return

        model_checkpoint = torch.load(self.classifier_path, map_location="cpu")
        run_conf = unflatten_dict(model_checkpoint["config"], ".")

        model = LinearClassifier(
            embed_dim=model_checkpoint["model_state_dict"]["fc1.weight"].shape[1],
            hidden_dim=run_conf["model"].get("hidden_dim", 100),
            num_classes=run_conf["data"]["num_classes"],
            drop_rate=0,
        )

        model.load_state_dict(model_checkpoint["model_state_dict"])
        model = model.to(self.device)
        model.eval()
        self.label_map = run_conf["data"]["label_map"]
        self.label_map = {int(k): v for k, v in self.label_map.items()}
        self.classifier = model

    def _load_inference_transforms(self):
        """Load the inference transformations from the run_configuration"""

        print(f"loading inference transforms")

        transform_settings = self.run_conf["transformations"]
        if "normalize" in transform_settings:
            mean = transform_settings["normalize"].get("mean", (0.5, 0.5, 0.5))
            std = transform_settings["normalize"].get("std", (0.5, 0.5, 0.5))
        else:
            mean = (0.5, 0.5, 0.5)
            std = (0.5, 0.5, 0.5)
        self.inference_transforms = T.Compose([T.ToTensor(), T.Normalize(mean=mean, std=std)])

    def remap_labels(self, cell_dicts):
        for cell_dict in cell_dicts:
            cell_dict["type"] = self.label_map[cell_dict["type"]]

    def _classify(self, predictions, cell_dicts):
        tokens = predictions["tokens"].detach().to("cpu")
        cell_tokens = []

        for idx, cell in enumerate(cell_dicts):
            patch_tokens = tokens[idx]
            bb_index = cell["bbox"] / self.run_conf["model"]["token_patch_size"]
            bb_index[0, :] = np.floor(bb_index[0, :])
            bb_index[1, :] = np.ceil(bb_index[1, :])
            bb_index = bb_index.astype(np.uint8)
            cell_token = patch_tokens[
                :, bb_index[0, 0] : bb_index[1, 0], bb_index[0, 1] : bb_index[1, 1]
            ]
            cell_token = torch.mean(rearrange(cell_token, "D H W -> (H W) D"), dim=0)
            cell_tokens.append(cell_token)

        cell_tokens_pt = torch.stack(cell_tokens)
        updated_preds = self.detection_cell_postprocessor.classifier(cell_tokens_pt)
        updated_preds = F.softmax(updated_preds, dim=1)
        updated_classes = torch.argmax(updated_preds, dim=1)
        updated_class_preds = updated_preds[torch.arange(updated_classes.shape[0]), updated_classes]

        for cell_dict, cls_id, cls_prob in zip(
            cell_dicts, updated_classes, updated_class_preds, strict=True
        ):
            cell_dict["type"] = int(cls_id)
            cell_dict["type_prob"] = float(cls_prob)

    def detect(self, wsi):

        self.frame_id += 1

        image_np = np.array(wsi)
        cv2.imshow("image_np", image_np)
        cv2.waitKey(1)

        with torch.no_grad():
            patches = self.inference_transforms(image_np)
            # patches = patches[None, :, :, :]
            patches = torch.unsqueeze(patches, 0)
            patches = patches.to(self.device)

            if self.mp:
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    predictions = self.model.forward(patches, retrieve_tokens=True)
            else:
                predictions = self.model.forward(patches, retrieve_tokens=True)
            predictions = self.apply_softmax_reorder(predictions)

        instance_mask, cell_dicts = self.postprocessor.post_process_batch(predictions)

        # self.check_outputs(instance_mask, cell_dicts)

        # one list of dicts for each image in batch - one dict in the list  for each cell in image
        cell_dicts = cell_dicts[0]
        cell_dicts = list(cell_dicts.values())

        if self.classifier is not None:
            self._classify(predictions, cell_dicts)

        return cell_dicts

    def check_outputs(self, instance_mask, cell_dicts):
        instance_mask = torch.squeeze(instance_mask).cpu().numpy()
        cell_ids = np.unique(instance_mask)
        invalid_idx = np.argwhere(cell_ids <= 0)
        cell_ids = np.delete(cell_ids, invalid_idx)
        n_cells = len(cell_ids)
        n_cell_dicts = len(cell_dicts)

        assert (
            n_cells == n_cell_dicts
        ), f"n_cells, n_cell_dicts mismatch ({n_cells}, {n_cell_dicts})"

        print(f"frame {self.frame_id} n_cells: {n_cells}")

    def apply_softmax_reorder(self, predictions: dict) -> dict:
        predictions["nuclei_binary_map"] = F.softmax(predictions["nuclei_binary_map"], dim=1)
        predictions["nuclei_type_map"] = F.softmax(predictions["nuclei_type_map"], dim=1)
        predictions["nuclei_type_map"] = predictions["nuclei_type_map"].permute(0, 2, 3, 1)
        predictions["nuclei_binary_map"] = predictions["nuclei_binary_map"].permute(0, 2, 3, 1)
        predictions["hv_map"] = predictions["hv_map"].permute(0, 2, 3, 1)
        return predictions
