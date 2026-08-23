"""
Verification suite for the pooled nucleus classifier.

Runs leave-one-slide-out to get honest out-of-fold predictions for every
nucleus, then analyses them four ways:

  1. Calibration      - does a stated confidence of 0.9 mean 90% correct?
  2. Error structure  - where do errors concentrate (slide, subtype, class,
                        cell size, annotation boundary)?
  3. Confidence gate  - what accuracy/coverage tradeoff does thresholding buy?
  4. Review sample    - a CSV of disagreements with WSI coordinates, for
                        Gilbert to open directly in QuPath.

Usage:
    python verify_model.py --root . --classes Tumor Stroma Immune
    python verify_model.py --root . --classes Tumor Stroma Immune --review_n 40
"""
import argparse
import glob
import os
from collections import Counter

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader, WeightedRandomSampler

NON_FEATURE_COLS = {
    "wsi_name", "nucleus_id", "cx_wsi", "cy_wsi", "label", "is_ground_truth",
    "containing_annotation_ids", "containing_annotation_classes",
    "annotation_nesting_depth",
}
DEFAULT_SUBTYPES = ["TNBC", "Cervix", "HNSCC", "NSCLC", "UpperGI",
                    "ER", "PR", "KI67"]


def collapse_label(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    raw = str(raw).strip()
    if raw == "" or raw.lower().startswith("ignore"):
        return None
    if raw == "Tumor":
        return "Tumor"
    if raw == "Stroma":
        return "Stroma"
    if raw == "Immune cells":
        return "Immune"
    if raw.startswith("Normal"):
        return "Normal"
    if raw in ("Necrosis", "Other"):
        return "Other"
    return None


class MLP(nn.Module):
    def __init__(self, n_features, n_classes, hidden=(48, 24, 12), dropout=0.3):
        super().__init__()
        layers, prev = [], n_features
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(dropout)]
            prev = h
        layers.append(nn.Linear(prev, n_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def fit_predict_proba(X_tr, y_tr, X_va, n_classes, args, device):
    mu, sd = X_tr.mean(0), X_tr.std(0)
    sd[sd == 0] = 1.0
    X_tr = ((X_tr - mu) / sd).astype(np.float32)
    X_va = ((X_va - mu) / sd).astype(np.float32)

    ds = TensorDataset(torch.from_numpy(X_tr), torch.from_numpy(y_tr))
    counts = Counter(y_tr.tolist())
    w = np.array([1.0 / (counts[int(t)] ** args.reweight_power) for t in y_tr])
    sampler = WeightedRandomSampler(torch.as_tensor(w, dtype=torch.double),
                                    num_samples=len(w), replacement=True)
    loader = DataLoader(ds, batch_size=args.batch_size, sampler=sampler,
                        drop_last=len(ds) > args.batch_size)

    model = MLP(X_tr.shape[1], n_classes, tuple(args.hidden), args.dropout).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    crit = nn.CrossEntropyLoss()
    for _ in range(args.epochs):
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            crit(model(xb), yb).backward()
            opt.step()

    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(X_va), 8192):
            chunk = torch.from_numpy(X_va[i:i + 8192]).to(device)
            out.append(torch.softmax(model(chunk), dim=1).cpu().numpy())
    return np.concatenate(out) if out else np.zeros((0, n_classes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--subtypes", nargs="+", default=DEFAULT_SUBTYPES)
    ap.add_argument("--classes", nargs="+", default=["Tumor", "Stroma", "Immune"])
    ap.add_argument("--review_n", type=int, default=30,
                    help="Disagreements per class-pair to include in the review CSV")
    ap.add_argument("--out_prefix", default="verify")
    ap.add_argument("--hidden", nargs="+", type=int, default=[48, 24, 12])
    ap.add_argument("--dropout", type=float, default=0.3)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight_decay", type=float, default=1e-3)
    ap.add_argument("--batch_size", type=int, default=256)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--reweight_power", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    classes = list(args.classes)
    c2i = {c: i for i, c in enumerate(classes)}

    frames = []
    for st in args.subtypes:
        paths = sorted(glob.glob(os.path.join(args.root, st, "*_gt_measurements.csv")))
        if not paths:
            continue
        sub = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
        sub["subtype"] = st
        sub["slide_uid"] = st + ":" + sub["wsi_name"].astype(str)
        frames.append(sub)
    if not frames:
        raise SystemExit("No data found.")

    df = pd.concat(frames, ignore_index=True)
    df["_label"] = df["label"].apply(collapse_label)
    df = df.dropna(subset=["_label"])
    df = df[df["_label"].isin(classes)].reset_index(drop=True)

    feat_cols = [c for c in df.columns
                 if c not in NON_FEATURE_COLS and not c.startswith("_")
                 and c not in ("subtype", "slide_uid")
                 and pd.api.types.is_numeric_dtype(df[c]) and df[c].notna().any()]
    df[feat_cols] = df[feat_cols].fillna(df[feat_cols].median())
    print(f"{len(df)} nuclei | {df['slide_uid'].nunique()} slides | {len(feat_cols)} features")

    X = df[feat_cols].to_numpy(dtype=np.float64)
    y = df["_label"].map(c2i).to_numpy()
    slide = df["slide_uid"].to_numpy()

    # Out-of-fold predictions: every nucleus scored by a model that never
    # saw its slide.
    print("\nRunning leave-one-slide-out for out-of-fold predictions...")
    proba = np.full((len(df), len(classes)), np.nan)
    for i, sl in enumerate(sorted(set(slide)), 1):
        te = slide == sl
        tr = ~te
        if len(set(y[tr])) < 2:
            continue
        proba[te] = fit_predict_proba(X[tr], y[tr], X[te], len(classes), args, device)
        if i % 10 == 0:
            print(f"  ...{i} slides")

    ok = ~np.isnan(proba[:, 0])
    df = df[ok].reset_index(drop=True)
    proba, y = proba[ok], y[ok]
    pred = proba.argmax(1)
    conf = proba.max(1)
    correct = pred == y

    df["_pred"] = [classes[p] for p in pred]
    df["_conf"] = conf
    df["_correct"] = correct

    from sklearn.metrics import f1_score, classification_report, confusion_matrix
    print("\n" + "=" * 70)
    print("OVERALL (out-of-fold)")
    print("=" * 70)
    print(f"acc={correct.mean():.4f}  "
          f"macro_f1={f1_score(y, pred, average='macro', zero_division=0):.4f}")
    print(classification_report(y, pred, labels=list(range(len(classes))),
                                target_names=classes, zero_division=0))

    # ---------------- 1. CALIBRATION ----------------
    print("=" * 70)
    print("1. CALIBRATION - is stated confidence trustworthy?")
    print("=" * 70)
    bins = np.linspace(0.0, 1.0, 11)
    print(f"{'confidence':>16} {'n':>8} {'predicted':>10} {'actual':>8} {'gap':>8}")
    ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (conf >= lo) & (conf < hi) if hi < 1.0 else (conf >= lo) & (conf <= hi)
        if m.sum() == 0:
            continue
        exp, act = conf[m].mean(), correct[m].mean()
        ece += (m.sum() / len(conf)) * abs(exp - act)
        flag = "  <-- overconfident" if exp - act > 0.1 else ""
        print(f"{lo:>7.1f}-{hi:<8.1f} {m.sum():>8} {exp:>10.3f} {act:>8.3f} "
              f"{exp-act:>+8.3f}{flag}")
    print(f"\nExpected Calibration Error: {ece:.4f}")
    print("  <0.05 well calibrated | 0.05-0.15 usable | >0.15 don't trust the number")

    # ---------------- 2. CONFIDENCE GATE ----------------
    print("\n" + "=" * 70)
    print("2. CONFIDENCE THRESHOLD - accuracy vs coverage")
    print("=" * 70)
    print(f"{'threshold':>10} {'kept':>8} {'coverage':>9} {'acc':>8} {'macro_f1':>9}")
    for t in [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
        m = conf >= t
        if m.sum() < 10:
            continue
        mf1 = f1_score(y[m], pred[m], average="macro",
                       labels=list(range(len(classes))), zero_division=0)
        print(f"{t:>10.2f} {m.sum():>8} {m.mean():>9.3f} "
              f"{correct[m].mean():>8.4f} {mf1:>9.4f}")

    # ---------------- 3. ERROR STRUCTURE ----------------
    print("\n" + "=" * 70)
    print("3. ERROR STRUCTURE")
    print("=" * 70)

    print("\nBy subtype:")
    print(f"{'subtype':>10} {'n':>8} {'acc':>8} {'mean_conf':>10} {'conf_when_wrong':>16}")
    for st, g in df.groupby("subtype"):
        wrong = g[~g["_correct"]]
        cw = wrong["_conf"].mean() if len(wrong) else float("nan")
        print(f"{st:>10} {len(g):>8} {g['_correct'].mean():>8.4f} "
              f"{g['_conf'].mean():>10.3f} {cw:>16.3f}")

    print("\nWorst 10 slides:")
    per_slide = df.groupby("slide_uid").agg(n=("_correct", "size"),
                                            acc=("_correct", "mean"),
                                            conf=("_conf", "mean"))
    for sl, r in per_slide.sort_values("acc").head(10).iterrows():
        print(f"  {sl:>22} n={int(r['n']):>6} acc={r['acc']:.4f} conf={r['conf']:.3f}")

    print("\nBy true class:")
    for c in classes:
        g = df[df["_label"] == c]
        if len(g) == 0:
            continue
        wrong = g[~g["_correct"]]
        top = Counter(wrong["_pred"]).most_common(2)
        print(f"  {c:>8} n={len(g):>7} acc={g['_correct'].mean():.4f} "
              f"| most confused with: {top}")

    # Nucleus size is the most interpretable feature - if errors cluster at
    # the extremes, that points at segmentation quality (debris / merged
    # clumps) rather than classification.
    if "area_um2" in df.columns:
        print("\nBy nucleus size (area_um2 quintile):")
        df["_size_bin"] = pd.qcut(df["area_um2"], 5, labels=False, duplicates="drop")
        for b, g in df.groupby("_size_bin"):
            print(f"  Q{int(b)+1} [{g['area_um2'].min():>6.1f}-{g['area_um2'].max():>6.1f} um2] "
                  f"n={len(g):>7} acc={g['_correct'].mean():.4f}")

    # Cells inside several nested annotations sit near region boundaries,
    # where region-derived labels are least reliable.
    if "annotation_nesting_depth" in df.columns:
        print("\nBy annotation nesting depth:")
        for d, g in df.groupby("annotation_nesting_depth"):
            if len(g) < 50:
                continue
            print(f"  depth={int(d)} n={len(g):>7} acc={g['_correct'].mean():.4f}")

    # ---------------- 4. REVIEW SAMPLE ----------------
    print("\n" + "=" * 70)
    print("4. REVIEW SAMPLE FOR PATHOLOGIST")
    print("=" * 70)
    rows = []
    for true_c in classes:
        for pred_c in classes:
            if true_c == pred_c:
                continue
            g = df[(df["_label"] == true_c) & (df["_pred"] == pred_c)]
            if len(g) == 0:
                continue
            # High-confidence disagreements are the informative ones: the
            # model is sure and the label says otherwise, so one of them is
            # wrong in a way worth understanding.
            g = g.nlargest(min(args.review_n, len(g)), "_conf")
            rows.append(g)
    if rows:
        review = pd.concat(rows, ignore_index=True)
        cols = ["subtype", "wsi_name", "cx_wsi", "cy_wsi", "_label", "_pred", "_conf"]
        cols = [c for c in cols if c in review.columns]
        review = review[cols].rename(columns={"_label": "annotation_says",
                                              "_pred": "model_says",
                                              "_conf": "model_confidence"})
        review["pathologist_verdict"] = ""
        review["notes"] = ""
        out = f"{args.out_prefix}_review_sample.csv"
        review.to_csv(out, index=False)
        print(f"Wrote {len(review)} high-confidence disagreements -> {out}")
        print("\nBreakdown:")
        for (a, m), g in review.groupby(["annotation_says", "model_says"]):
            print(f"  annotation={a:<8} model={m:<8} n={len(g):>4} "
                  f"mean_conf={g['model_confidence'].mean():.3f}")
        print("\nFor each row, go to (cx_wsi, cy_wsi) in QuPath and record")
        print("whether the annotation or the model is correct in "
              "'pathologist_verdict'.")

    full = f"{args.out_prefix}_all_predictions.csv"
    keep = [c for c in ["subtype", "wsi_name", "nucleus_id", "cx_wsi", "cy_wsi",
                        "_label", "_pred", "_conf", "_correct"] if c in df.columns]
    df[keep].to_csv(full, index=False)
    print(f"\nAll out-of-fold predictions -> {full}")


if __name__ == "__main__":
    main()