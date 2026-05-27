"""
Evaluation module — generates all quantitative results needed for the paper.

Outputs:
  data/evaluation_report.txt   — classification report + ablation table
  data/confusion_matrix.csv    — raw confusion matrix values
  data/threshold_curve.csv     — F1/precision/recall across thresholds 0.5–0.99
  data/ablation.csv            — per-perspective F1 vs composite F1
"""

import os
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)

THRESHOLD = 0.875   # must match fusion.py


def _binary(scores: pd.Series, threshold: float) -> pd.Series:
    return (scores < threshold).astype(int)


def run_evaluation(results_path: str = "data/results.csv") -> None:
    df = pd.read_csv(results_path)
    y_true = df["is_anomaly"].astype(int)

    os.makedirs("data", exist_ok=True)
    lines = []

    # ── 1. Primary classification report (composite score) ────
    y_pred = _binary(df["composite_score"], THRESHOLD)

    report = classification_report(
        y_true, y_pred,
        target_names=["Normal", "Anomaly"],
        digits=4,
    )
    lines.append("=" * 60)
    lines.append("  CLASSIFICATION REPORT — Composite (min-score) @ 0.875")
    lines.append("=" * 60)
    lines.append(report)

    # ── 2. Per-attack-type breakdown ──────────────────────────
    lines.append("─" * 60)
    lines.append("  PER-ATTACK-TYPE DETECTION")
    lines.append("─" * 60)
    for attack in df[df["is_anomaly"] == True]["attack_type"].unique():
        subset = df[df["attack_type"] == attack]
        detected = (subset["flagged"] == True).sum()
        lines.append(f"  {attack:<25} {detected:>2}/{len(subset)} detected"
                     f"  avg_score={subset['composite_score'].mean():.4f}")
    lines.append("")

    # ── 3. Ablation — each perspective alone vs composite ─────
    lines.append("─" * 60)
    lines.append("  ABLATION STUDY  (F1 score at threshold 0.875)")
    lines.append("─" * 60)

    ablation_rows = []
    perspectives = {
        "Control Flow only":  "cf_score",
        "Time only":          "time_score",
        "Resource only":      "resource_score",
        "Amount only":        "amount_score",
        "Weighted Average":   "weighted_avg_score",
        "Composite (min)":    "composite_score",
    }
    for label, col in perspectives.items():
        pred = _binary(df[col], THRESHOLD)
        p = precision_score(y_true, pred, zero_division=0)
        r = recall_score(y_true, pred, zero_division=0)
        f = f1_score(y_true, pred, zero_division=0)
        fp = int(((pred == 1) & (y_true == 0)).sum())
        fn = int(((pred == 0) & (y_true == 1)).sum())
        lines.append(f"  {label:<22}  P={p:.4f}  R={r:.4f}  F1={f:.4f}"
                     f"  FP={fp}  FN={fn}")
        ablation_rows.append({"perspective": label, "precision": round(p,4),
                               "recall": round(r,4), "f1": round(f,4),
                               "false_positives": fp, "false_negatives": fn})

    pd.DataFrame(ablation_rows).to_csv("data/ablation.csv", index=False)
    lines.append("")

    # ── 4. Threshold sensitivity curve ────────────────────────
    thresholds = np.round(np.arange(0.50, 1.00, 0.01), 2)
    curve_rows = []
    for t in thresholds:
        pred = _binary(df["composite_score"], float(t))
        curve_rows.append({
            "threshold":  round(float(t), 2),
            "precision":  round(precision_score(y_true, pred, zero_division=0), 4),
            "recall":     round(recall_score(y_true, pred, zero_division=0), 4),
            "f1":         round(f1_score(y_true, pred, zero_division=0), 4),
        })
    curve_df = pd.DataFrame(curve_rows)
    curve_df.to_csv("data/threshold_curve.csv", index=False)

    best = curve_df.loc[curve_df["f1"].idxmax()]
    lines.append("─" * 60)
    lines.append("  THRESHOLD SENSITIVITY")
    lines.append("─" * 60)
    lines.append(f"  Best F1={best['f1']:.4f} at threshold={best['threshold']}")
    closest_idx = (curve_df["threshold"] - THRESHOLD).abs().idxmin()
    chosen_f1   = curve_df.loc[closest_idx, "f1"]
    lines.append(f"  Chosen threshold={THRESHOLD}  F1≈{chosen_f1:.4f}")
    lines.append("  Full curve saved → data/threshold_curve.csv")
    lines.append("")

    # ── 5. Confusion matrix ───────────────────────────────────
    cm = confusion_matrix(y_true, y_pred)
    cm_df = pd.DataFrame(
        cm,
        index=["Actual Normal", "Actual Anomaly"],
        columns=["Predicted Normal", "Predicted Anomaly"],
    )
    cm_df.to_csv("data/confusion_matrix.csv")

    lines.append("─" * 60)
    lines.append("  CONFUSION MATRIX")
    lines.append("─" * 60)
    lines.append(f"  TN={cm[0,0]}  FP={cm[0,1]}  FN={cm[1,0]}  TP={cm[1,1]}")
    lines.append("")

    # ── Write report ──────────────────────────────────────────
    report_text = "\n".join(lines)
    with open("data/evaluation_report.txt", "w") as f:
        f.write(report_text)

    print(report_text)
    print("  Saved → data/evaluation_report.txt")
    print("  Saved → data/confusion_matrix.csv")
    print("  Saved → data/threshold_curve.csv")
    print("  Saved → data/ablation.csv")


if __name__ == "__main__":
    run_evaluation()
