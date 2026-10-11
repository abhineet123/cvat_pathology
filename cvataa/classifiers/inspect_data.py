"""
Inspects the exported nucleus measurements BEFORE training, to check
whether the features can plausibly separate the classes at all.

Usage:
    python inspect_data.py --root /path/to/project
    python inspect_data.py --root /path/to/project --val_slides D1 C7
"""
import argparse
import glob
import os

import numpy as np
import pandas as pd

CLASSES = ["Tumor", "Stroma", "Immune", "Normal", "Other"]

NON_FEATURE_COLS = {
    "wsi_name", "nucleus_id", "cx_wsi", "cy_wsi", "label", "is_ground_truth",
    "containing_annotation_ids", "containing_annotation_classes",
    "annotation_nesting_depth",
}


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--val_slides", nargs="+", default=None)
    ap.add_argument("--top_n", type=int, default=15)
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.root,
                                          "*_gt_measurements.csv")))
    if not paths:
        raise SystemExit(f"No CSVs found under {args.root}/ground_truth_measurements/")

    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    df["_label"] = df["label"].apply(collapse_label)
    df = df.dropna(subset=["_label"]).reset_index(drop=True)

    print("=" * 78)
    print(f"{len(df)} nuclei | {df['wsi_name'].nunique()} slides | {len(paths)} CSVs")
    print("=" * 78)

    # ---------------- 1. CLASS DISTRIBUTION PER SLIDE ----------------
    print("\n### 1. CLASS COUNTS PER SLIDE")
    pivot = df.pivot_table(index="wsi_name", columns="_label", aggfunc="size", fill_value=0)
    for c in CLASSES:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot = pivot[CLASSES]
    pivot["TOTAL"] = pivot.sum(axis=1)
    print(pivot.to_string())

    print("\nOverall:")
    tot = df["_label"].value_counts()
    for c in CLASSES:
        n = int(tot.get(c, 0))
        print(f"  {c:<8} {n:>8}  ({100*n/len(df):5.1f}%)  "
              f"present on {int((pivot[c] > 0).sum())}/{len(pivot)} slides")

    # A class confined to few slides can't generalize: the model learns that
    # slide's staining rather than the class.
    print("\n  ! Classes on <3 slides cannot be learned in a slide-split setting:")
    for c in CLASSES:
        ns = int((pivot[c] > 0).sum())
        if 0 < ns < 3:
            print(f"      {c}: only {ns} slide(s)")

    # ---------------- 2. FEATURE SANITY ----------------
    feat_cols = [c for c in df.columns
                 if c not in NON_FEATURE_COLS and not c.startswith("_")
                 and pd.api.types.is_numeric_dtype(df[c])]
    print(f"\n### 2. FEATURE SANITY ({len(feat_cols)} numeric features)")
    problems = []
    for c in feat_cols:
        col = df[c]
        nan_frac = col.isna().mean()
        if nan_frac > 0.5:
            problems.append(f"  {c}: {100*nan_frac:.0f}% NaN")
        elif col.nunique(dropna=True) <= 1:
            problems.append(f"  {c}: constant value")
    if problems:
        print("\n".join(problems))
    else:
        print("  No all-NaN or constant features.")

    # ---------------- 3. PER-CLASS SEPARABILITY ----------------
    # F-statistic: between-class variance / within-class variance. Low values
    # across the board mean the features simply don't distinguish the classes.
    print(f"\n### 3. TOP {args.top_n} FEATURES BY CLASS SEPARABILITY (ANOVA F)")
    from sklearn.feature_selection import f_classif
    X = df[feat_cols].to_numpy(dtype=np.float64)
    med = np.nanmedian(X, axis=0)
    med = np.where(np.isnan(med), 0.0, med)
    X = np.where(np.isnan(X), med, X)
    y = df["_label"].to_numpy()
    F, p = f_classif(X, y)
    order = np.argsort(-np.nan_to_num(F))
    for i in order[:args.top_n]:
        print(f"  {feat_cols[i]:<45} F={F[i]:>12.1f}  p={p[i]:.2e}")
    print(f"\n  Median F across all features: {np.nanmedian(F):.1f}")

    # ---------------- 4. TUMOR vs REST ----------------
    print("\n### 4. TUMOR vs EVERYTHING ELSE (mean +/- std)")
    is_tumor = df["_label"] == "Tumor"
    rows = []
    for c in feat_cols:
        a, b = df.loc[is_tumor, c], df.loc[~is_tumor, c]
        if a.notna().sum() < 10 or b.notna().sum() < 10:
            continue
        pooled = np.sqrt((a.var() + b.var()) / 2)
        d = (a.mean() - b.mean()) / pooled if pooled > 0 else 0.0
        rows.append((abs(d), c, a.mean(), a.std(), b.mean(), b.std(), d))
    rows.sort(reverse=True)
    print(f"  {'feature':<45} {'tumor':>18} {'other':>18} {'cohen_d':>8}")
    for _, c, am, asd, bm, bsd, d in rows[:args.top_n]:
        print(f"  {c:<45} {am:>9.3f}+/-{asd:<7.3f} {bm:>9.3f}+/-{bsd:<7.3f} {d:>8.2f}")
    if rows:
        print(f"\n  Largest |Cohen's d| = {rows[0][0]:.2f}  "
              f"(<0.2 negligible, 0.5 medium, >0.8 large)")

    # ---------------- 5. SLIDE EFFECT ----------------
    # If a feature varies more BETWEEN slides than between classes, the model
    # will key on slide identity and fail to transfer to held-out slides.
    print("\n### 5. SLIDE EFFECT vs CLASS EFFECT")
    F_slide, _ = f_classif(X, df["wsi_name"].to_numpy())
    ratio = np.nan_to_num(F_slide) / np.maximum(np.nan_to_num(F), 1e-9)
    worst = np.argsort(-ratio)
    print(f"  {'feature':<45} {'F_slide':>12} {'F_class':>12} {'ratio':>8}")
    for i in worst[:args.top_n]:
        print(f"  {feat_cols[i]:<45} {F_slide[i]:>12.1f} {F[i]:>12.1f} {ratio[i]:>8.1f}")
    n_dominated = int((ratio > 1).sum())
    print(f"\n  {n_dominated}/{len(feat_cols)} features vary more between SLIDES "
          f"than between CLASSES.")
    if n_dominated > len(feat_cols) * 0.5:
        print("  -> Batch/staining effect dominates. Per-slide normalization is likely "
              "needed\n     before a slide-split model can transfer.")

    # ---------------- 6. QUICK BASELINE ----------------
    print("\n### 6. QUICK BASELINE (random forest, slide-split)")
    if args.val_slides:
        val_mask = df["wsi_name"].isin(args.val_slides).to_numpy()
    else:
        slides = sorted(df["wsi_name"].unique())
        val_mask = df["wsi_name"].isin(slides[:2]).to_numpy()
        print(f"  (no --val_slides given; using {slides[:2]})")

    if val_mask.sum() == 0 or (~val_mask).sum() == 0:
        print("  Cannot split - check slide names.")
        return

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, confusion_matrix, f1_score
    rf = RandomForestClassifier(n_estimators=200, class_weight="balanced",
                                random_state=0, n_jobs=-1)
    rf.fit(X[~val_mask], y[~val_mask])

    tr_pred = rf.predict(X[~val_mask])
    va_pred = rf.predict(X[val_mask])
    print(f"  TRAIN acc={np.mean(tr_pred == y[~val_mask]):.4f}  "
          f"macro_f1={f1_score(y[~val_mask], tr_pred, average='macro', zero_division=0):.4f}")
    print(f"  VAL   acc={np.mean(va_pred == y[val_mask]):.4f}  "
          f"macro_f1={f1_score(y[val_mask], va_pred, average='macro', zero_division=0):.4f}")
    print("\n" + classification_report(y[val_mask], va_pred, zero_division=0))

    labs = sorted(set(y))
    cm = confusion_matrix(y[val_mask], va_pred, labels=labs)
    print("Confusion (rows=true, cols=pred): " + "  ".join(labs))
    for i, r in enumerate(cm):
        print(f"{labs[i]:>8}: " + " ".join(f"{v:7d}" for v in r))

    print("\n  If TRAIN is high but VAL is near chance, the features encode slide "
          "identity\n  rather than cell class - the same failure the MLP showed.")

    print("\n### TOP FEATURE IMPORTANCES")
    imp = np.argsort(-rf.feature_importances_)
    for i in imp[:args.top_n]:
        print(f"  {feat_cols[i]:<45} {rf.feature_importances_[i]:.4f}")


if __name__ == "__main__":
    main()