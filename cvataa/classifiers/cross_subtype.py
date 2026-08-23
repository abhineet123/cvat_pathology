"""
Cross-subtype experiment on QuPath nucleus measurements.

Directory layout expected (run from the directory containing these):
    TNBC/*_gt_measurements.csv
    Cervix/*_gt_measurements.csv
    HNSCC/*_gt_measurements.csv
    NSCLC/*_gt_measurements.csv
    UpperGI/*_gt_measurements.csv

Three experiments:

  loso   Leave-one-SUBTYPE-out. Train on 4 subtypes, test on the held-out
         one. Answers: does a model trained on other tissue types transfer
         to an unseen one?

  pooled Leave-one-SLIDE-out, but training on all subtypes' slides. Compare
         each subtype's score here against its own single-subtype baseline
         to see whether extra cross-subtype data helps or hurts.

  both   Runs both (default).

Usage:
    python cross_subtype.py --classes Tumor Stroma
    python cross_subtype.py --classes Tumor Stroma Immune --experiment loso
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
from sklearn.metrics import f1_score, classification_report, confusion_matrix

NON_FEATURE_COLS = {
    "wsi_name", "nucleus_id", "cx_wsi", "cy_wsi", "label", "is_ground_truth",
    "containing_annotation_ids", "containing_annotation_classes",
    "annotation_nesting_depth",
}
DEFAULT_SUBTYPES = ["TNBC", "Cervix", "HNSCC", "NSCLC", "UpperGI"]


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


def load_subtypes(root, subtypes, keep_classes):
    frames = []
    for st in subtypes:
        d = os.path.join(root, st)
        if not os.path.isdir(d):
            print(f"  skipping {st}: directory not found")
            continue
        # CSVs sit directly in the subtype directory (no nested subfolder).
        paths = sorted(glob.glob(os.path.join(d, "*_gt_measurements.csv")))
        if not paths:
            print(f"  skipping {st}: no *_gt_measurements.csv")
            continue
        sub = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
        sub["subtype"] = st
        # Slide names can collide across subtypes (e.g. C10 in Cervix and
        # D10 in TNBC are distinct, but nothing guarantees uniqueness) -
        # prefix so slide-level grouping never merges two different slides.
        sub["slide_uid"] = st + ":" + sub["wsi_name"].astype(str)
        frames.append(sub)
        print(f"  {st}: {len(paths)} slides, {len(sub)} nuclei")
    if not frames:
        raise SystemExit("No data loaded.")

    df = pd.concat(frames, ignore_index=True)
    df["_label"] = df["label"].apply(collapse_label)
    df = df.dropna(subset=["_label"])
    df = df[df["_label"].isin(keep_classes)].reset_index(drop=True)
    return df


def get_feature_cols(df):
    cols = []
    for c in df.columns:
        if c in NON_FEATURE_COLS or c.startswith("_") or c in ("subtype", "slide_uid"):
            continue
        if not pd.api.types.is_numeric_dtype(df[c]):
            continue
        if df[c].isna().all():
            continue
        cols.append(c)
    return cols


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


def fit_predict(X_tr, y_tr, X_va, n_classes, args, device):
    """Standardization uses TRAIN statistics only - fitting on the combined
    set would leak the held-out distribution."""
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
    preds = []
    with torch.no_grad():
        for i in range(0, len(X_va), 4096):
            chunk = torch.from_numpy(X_va[i:i + 4096]).to(device)
            preds.append(model(chunk).argmax(1).cpu().numpy())
    return np.concatenate(preds) if preds else np.array([])


def summarize(y_true, y_pred, classes, title):
    print(f"\n--- {title} (n={len(y_true)}) ---")
    acc = (y_pred == y_true).mean()
    mf1 = f1_score(y_true, y_pred, average="macro",
                   labels=list(range(len(classes))), zero_division=0)
    print(f"acc={acc:.4f}  macro_f1={mf1:.4f}")
    print(classification_report(y_true, y_pred, labels=list(range(len(classes))),
                                target_names=classes, zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(classes))))
    print("Confusion (rows=true, cols=pred): " + "  ".join(classes))
    for i, r in enumerate(cm):
        print(f"{classes[i]:>8}: " + " ".join(f"{v:7d}" for v in r))
    return acc, mf1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Directory containing subtype folders")
    ap.add_argument("--subtypes", nargs="+", default=DEFAULT_SUBTYPES)
    ap.add_argument("--classes", nargs="+", default=["Tumor", "Stroma"])
    ap.add_argument("--experiment", choices=["loso", "pooled", "both"], default="both")
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
    print(f"Device: {device}  |  classes: {args.classes}")

    classes = list(args.classes)
    c2i = {c: i for i, c in enumerate(classes)}

    print("\nLoading:")
    df = load_subtypes(args.root, args.subtypes, classes)
    feat_cols = get_feature_cols(df)
    df[feat_cols] = df[feat_cols].fillna(df[feat_cols].median())
    print(f"\nTotal: {len(df)} nuclei | {df['slide_uid'].nunique()} slides | "
          f"{df['subtype'].nunique()} subtypes | {len(feat_cols)} features")

    print("\nClass counts by subtype:")
    print(df.pivot_table(index="subtype", columns="_label", aggfunc="size",
                         fill_value=0).to_string())

    X = df[feat_cols].to_numpy(dtype=np.float64)
    y = df["_label"].map(c2i).to_numpy()
    subtype = df["subtype"].to_numpy()
    slide = df["slide_uid"].to_numpy()

    # ---------------- Leave-one-SUBTYPE-out ----------------
    if args.experiment in ("loso", "both"):
        print("\n" + "=" * 70)
        print("EXPERIMENT 1: LEAVE-ONE-SUBTYPE-OUT")
        print("Train on 4 subtypes, test on the 5th. Tests transfer to unseen tissue.")
        print("=" * 70)
        print(f"{'held-out':>10} {'n_test':>8} {'n_train':>9} {'acc':>8} {'macro_f1':>9}")
        rows = []
        for st in sorted(set(subtype)):
            te = subtype == st
            tr = ~te
            if len(set(y[tr])) < 2 or len(set(y[te])) < 2:
                print(f"{st:>10} skipped (need >=2 classes in both splits)")
                continue
            pred = fit_predict(X[tr], y[tr], X[te], len(classes), args, device)
            acc = (pred == y[te]).mean()
            mf1 = f1_score(y[te], pred, average="macro",
                           labels=list(range(len(classes))), zero_division=0)
            print(f"{st:>10} {te.sum():>8} {tr.sum():>9} {acc:>8.4f} {mf1:>9.4f}")
            rows.append((st, acc, mf1, y[te].copy(), pred))
        if rows:
            a = np.array([r[1] for r in rows])
            f = np.array([r[2] for r in rows])
            print(f"\nMean: acc={a.mean():.4f}+/-{a.std():.4f}  "
                  f"macro_f1={f.mean():.4f}+/-{f.std():.4f}")
            summarize(np.concatenate([r[3] for r in rows]),
                      np.concatenate([r[4] for r in rows]),
                      classes, "POOLED ACROSS HELD-OUT SUBTYPES")

    # ---------------- Pooled training, leave-one-SLIDE-out ----------------
    if args.experiment in ("pooled", "both"):
        print("\n" + "=" * 70)
        print("EXPERIMENT 2: POOLED TRAINING, LEAVE-ONE-SLIDE-OUT")
        print("Each fold holds out one slide; training uses every other slide")
        print("from ALL subtypes. Compare per-subtype scores against the")
        print("single-subtype baselines to see if pooling helps.")
        print("=" * 70)

        all_true, all_pred, all_st = [], [], []
        for i, sl in enumerate(sorted(set(slide)), 1):
            te = slide == sl
            tr = ~te
            if len(set(y[te])) < 2:
                continue
            pred = fit_predict(X[tr], y[tr], X[te], len(classes), args, device)
            all_true.append(y[te])
            all_pred.append(pred)
            all_st.append(subtype[te])
            if i % 10 == 0:
                print(f"  ...{i} slides done")

        if all_true:
            yt = np.concatenate(all_true)
            yp = np.concatenate(all_pred)
            st_arr = np.concatenate(all_st)
            print(f"\n{'subtype':>10} {'n':>8} {'acc':>8} {'macro_f1':>9}")
            for st in sorted(set(st_arr)):
                m = st_arr == st
                acc = (yp[m] == yt[m]).mean()
                mf1 = f1_score(yt[m], yp[m], average="macro",
                               labels=list(range(len(classes))), zero_division=0)
                print(f"{st:>10} {m.sum():>8} {acc:>8.4f} {mf1:>9.4f}")
            summarize(yt, yp, classes, "POOLED-TRAINED, ALL SLIDES")


if __name__ == "__main__":
    main()