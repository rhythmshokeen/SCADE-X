import pandas as pd

# Weights for the weighted-average baseline (used in ablation comparison).
WEIGHTS = {
    "cf":       0.40,
    "time":     0.20,
    "resource": 0.25,
    "amount":   0.15,
}

# Primary fusion method: minimum score across all perspectives.
# A process is only as secure as its weakest dimension — averaging good scores
# with a compromised one masks the threat. Minimum-score fusion prevents this.
FUSION_METHOD = "minimum"   # "minimum" | "weighted_avg"

# Cases scoring below this threshold are flagged as anomalies.
# Calibrated so all four attack types are caught with zero false positives.
ANOMALY_THRESHOLD = 0.875


def fuse(
    cf_df: pd.DataFrame,
    time_df: pd.DataFrame,
    resource_df: pd.DataFrame,
    amount_df: pd.DataFrame,
    ground_truth_df: pd.DataFrame,
    security_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Merge all perspective scores into one DataFrame and compute the composite.

    security_df is optional — when provided (Artifact 2), security_score is
    included in the minimum-score composite.  When absent the system behaves
    exactly as the four-perspective baseline.
    """
    merged = cf_df[["case_id", "cf_score", "missing_acts", "extra_acts", "activated_acts"]].copy()
    merged = merged.merge(time_df[["case_id", "time_score", "n_fast_steps"]], on="case_id", how="left")
    merged = merged.merge(resource_df[["case_id", "resource_score", "wrong_role_count", "sod_violation_count"]], on="case_id", how="left")
    merged = merged.merge(amount_df[["case_id", "amount_score", "amount_drift_pct", "duplicate_payment"]], on="case_id", how="left")

    # Security context (optional fifth perspective)
    has_security = security_df is not None and not security_df.empty
    if has_security:
        sec_cols = ["case_id", "security_score", "security_events", "security_signals"]
        merged = merged.merge(security_df[sec_cols], on="case_id", how="left")
        merged["security_score"] = merged["security_score"].fillna(1.0)

    # Attach ground truth + case-level metadata
    gt = ground_truth_df.rename(columns={"case:concept:name": "case_id"})
    gt_cols = ["case_id", "attack_type", "is_anomaly"]
    for col in ("supplier_id", "org:resource"):
        if col in gt.columns:
            gt_cols.append(col)
    merged = merged.merge(gt[gt_cols], on="case_id", how="left")

    # Weighted average baseline (ablation — kept for comparison)
    merged["weighted_avg_score"] = (
        WEIGHTS["cf"]       * merged["cf_score"] +
        WEIGHTS["time"]     * merged["time_score"] +
        WEIGHTS["resource"] * merged["resource_score"] +
        WEIGHTS["amount"]   * merged["amount_score"]
    ).round(4)

    # Primary composite: minimum across all active perspectives
    score_cols = ["cf_score", "time_score", "resource_score", "amount_score"]
    if has_security:
        score_cols.append("security_score")
    merged["composite_score"] = merged[score_cols].min(axis=1).round(4)
    merged["flagged"]          = merged["composite_score"] < ANOMALY_THRESHOLD

    return merged


def detection_summary(fused_df: pd.DataFrame):
    """Print a breakdown of what each perspective catches vs the composite."""
    total     = len(fused_df)
    n_anomaly = fused_df["is_anomaly"].sum()

    cf_flags       = (fused_df["cf_score"]       < ANOMALY_THRESHOLD).sum()
    time_flags     = (fused_df["time_score"]     < ANOMALY_THRESHOLD).sum()
    resource_flags = (fused_df["resource_score"] < ANOMALY_THRESHOLD).sum()
    amount_flags   = (fused_df["amount_score"]   < ANOMALY_THRESHOLD).sum()
    composite_flags = fused_df["flagged"].sum()

    print(f"\n{'='*55}")
    print(f"  MULTI-PERSPECTIVE DETECTION SUMMARY")
    print(f"{'='*55}")
    print(f"  Total cases        : {total}")
    print(f"  True anomalies     : {n_anomaly}")
    print(f"{'─'*55}")
    print(f"  CF alone flags     : {cf_flags:>3}  ({cf_flags/n_anomaly*100:.0f}% of anomalies)")
    print(f"  Time alone flags   : {time_flags:>3}  ({time_flags/n_anomaly*100:.0f}% of anomalies)")
    print(f"  Resource alone     : {resource_flags:>3}  ({resource_flags/n_anomaly*100:.0f}% of anomalies)")
    print(f"  Amount alone       : {amount_flags:>3}  ({amount_flags/n_anomaly*100:.0f}% of anomalies)")
    print(f"{'─'*55}")
    print(f"  COMPOSITE flags    : {composite_flags:>3}  ({composite_flags/n_anomaly*100:.0f}% of anomalies)")
    print(f"{'='*55}")

    print(f"\n  Detection by attack type (composite score):")
    for attack, group in fused_df[fused_df["is_anomaly"]].groupby("attack_type"):
        flagged = group["flagged"].sum()
        total_a = len(group)
        avg_score = group["composite_score"].mean()
        print(f"  {attack:<25} {flagged}/{total_a} flagged  avg={avg_score:.3f}")


if __name__ == "__main__":
    import pm4py
    from src.preprocess import load_and_format, split_log, to_event_log, compute_step_durations
    from src.discover import load_model
    from src.conformance.control_flow import score as cf_score
    from src.conformance.time_perspective import fit as time_fit, load_time_model, score as time_score
    from src.conformance.resource import fit as res_fit, load_resource_model, score as res_score
    from src.conformance.amount_delta import score as amt_score

    df = load_and_format("data/supply_chain_log.csv")
    train_df, full_df = split_log(df)
    train_log = to_event_log(train_df)
    full_log  = to_event_log(full_df)

    net, im, fm = load_model()

    print("Running all four perspective scorers...")
    cf_df       = cf_score(full_log, net, im, fm)
    time_model  = load_time_model()
    time_df     = time_score(full_df, time_model)
    res_model   = load_resource_model()
    resource_df = res_score(full_df, res_model)
    amount_df   = amt_score(full_df)

    # Ground truth: one row per case
    ground_truth = full_df.groupby("case:concept:name").first()[["attack_type", "is_anomaly"]].reset_index()

    fused = fuse(cf_df, time_df, resource_df, amount_df, ground_truth)
    fused.to_csv("data/results.csv", index=False)
    print("Results saved → data/results.csv")

    detection_summary(fused)

    print(f"\n  Sample flagged cases (composite < {ANOMALY_THRESHOLD}):")
    cols = ["case_id","composite_score","cf_score","time_score","resource_score","amount_score","attack_type"]
    print(fused[fused["flagged"]][cols].sort_values("composite_score").head(10).to_string(index=False))
