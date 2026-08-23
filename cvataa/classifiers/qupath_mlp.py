import numpy as np
import os
import pandas as pd
import torch
import torch.nn as nn

from tqdm import tqdm

from classifiers.cell_cls_params import QuPathMLPParams

from classifiers.extract_features import NucleusFeatureExtractor, add_smoothed_features

import cell_seg_utils as utils


class MLP(nn.Module):
    def __init__(self, n_features, n_classes, hidden, dropout, device):
        super().__init__()
        self.device = device
        layers, prev = [], n_features
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, n_classes))
        self.net = nn.Sequential(*layers)
        self.net.to(self.device)

    def forward(self, x):
        return self.net(x.to(self.device))


class QuPathMLP:
    def __init__(self, params: QuPathMLPParams):
        self.params = params
        self.ckpt_path = self.params.ckpt_path
        if params.ckpt_root:
            self.ckpt_path = utils.linux_path(params.ckpt_root, self.ckpt_path)

        assert self.ckpt_path, "ckpt_path must be provided"

        self.device = "cuda" if self.params.gpu and torch.cuda.is_available() else "cpu"

        print(f"loading QuPathMLP ckpt from: {self.ckpt_path}")
        self.ckpt = torch.load(self.ckpt_path, map_location="cpu", weights_only=False)
        self.classes = self.ckpt["classes"]
        self.feat_cols = self.ckpt["feature_cols"]
        self.n_features = len(self.feat_cols)
        self.n_classes = len(self.classes)

        self.class_names = self.ckpt.get("qupath_names", self.classes)
        self.mu, self.sd = np.asarray(self.ckpt["mu"]), np.asarray(self.ckpt["sd"])
        self.medians = np.asarray(self.ckpt["medians"])

        self.sd_safe = self.sd.copy()
        self.sd_safe[self.sd_safe == 0] = 1.0

        self.model = MLP(
            n_features=self.n_features,
            n_classes=self.n_classes,
            hidden=tuple(self.ckpt["hidden"]),
            dropout=self.ckpt["dropout"],
            device=self.device,
        )
        self.model.load_state_dict(self.ckpt["model_state"])
        self.model.eval()

        self.name = "qmlp"
        if self.params.suffixes:
            name_suffix = "-".join(self.params.suffixes)
            self.name = f"{self.name}-{name_suffix}"

    def _fix_nan(self, feats, medians):
        nan_frac = np.isnan(feats).mean()
        if nan_frac > 0.5:
            raise AssertionError(
                f"{100*nan_frac:.0f}% of feature values are missing. "
                f"Features were probably never computed on this image.",
            )
        if nan_frac > 0:
            print(f"Note: filling {100*nan_frac:.2f}% missing values with training medians")
        feats = np.where(np.isnan(feats), medians, feats)
        return feats

    def classify(self, wsi_path: str, nuclei: list, cache_path: str):

        n_nuclei = len(nuclei)

        self.ext = NucleusFeatureExtractor(wsi_path)

        base_feats_csv = utils.linux_path(cache_path, "base_features.csv")
        all_feats_csv = utils.linux_path(cache_path, "all_features.csv")

        base_feats = all_feats = None

        if os.path.isfile(all_feats_csv):
            print(f"loading all_features from {all_feats_csv}")
            all_feats = pd.read_csv(all_feats_csv)
        elif os.path.isfile(base_feats_csv):
            print(f"loading base_features from {all_feats_csv}")
            base_feats = pd.read_csv(base_feats_csv)
            centroids = np.asarray([np.mean(poly) for poly in nuclei])

        # for poly in nuclei:
        #     feats = self.ext.extract_one(poly)

        if all_feats is None:
            if base_feats is None:
                base_feats, centroids = self.ext.extract_many(nuclei)
                print(f"saving base_features to {base_feats_csv}")
                base_feats.to_csv(base_feats_csv, index=False)

            # smoothed features need the whole population (they average over
            # neighbours), so they are a separate pass over the base table
            all_feats = add_smoothed_features(base_feats, centroids, self.ext.mpp)
            print(f"saving all_features to {all_feats_csv}")
            all_feats.to_csv(all_feats_csv, index=False)

        all_feats_arr = all_feats[self.feat_cols].to_numpy(dtype=np.float32)
        n_feats = len(all_feats_arr)

        assert n_nuclei == n_feats, "mismatch between n_feats and n_nuclei"

        # self._fix_nan(feats, self.medians)

        all_feats_arr = ((all_feats_arr - self.mu) / self.sd_safe).astype(np.float32)

        probs = []
        with torch.no_grad():
            for i in tqdm(range(0, n_nuclei, self.params.batch_size), desc="MLP"):
                batch_feats = all_feats_arr[i : i + self.params.batch_size]
                out = self.model(torch.from_numpy(batch_feats))
                probs.append(torch.softmax(out, dim=1).cpu().numpy())

        probs = np.concatenate(probs) if probs else np.zeros((0, self.n_classes))

        n_probs = len(probs)
        assert n_probs == n_nuclei, "n_probs does not match n_nuclei"

        pred_idx = probs.argmax(1)
        n_preds = len(pred_idx)
        assert n_preds == n_nuclei, "n_preds does not match n_nuclei"

        confidence = probs.max(1)
        n_conf = len(confidence)
        assert n_conf == n_nuclei, "n_conf does not match n_nuclei"

        n_low = 0
        nuclei_classes = []
        pbar = tqdm(range(n_nuclei))
        for i in pbar:
            conf = float(confidence[i])
            if conf < self.params.min_conf > 0:
                name = "unclassified"
                n_low += 1
            else:
                name = self.class_names[pred_idx[i]]
            nuclei_classes.append(
                {
                    "cls": name,
                    "conf": round(conf, 4),
                }
            )
            pbar.set_description(f"post processing: n_low: {n_low}")
        return nuclei_classes
