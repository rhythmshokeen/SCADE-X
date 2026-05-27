"""
Cross-case correlation — the second detection layer.

Individual conformance scoring treats each case in isolation.
This module looks across all flagged cases to surface:

  1. Supplier risk   — same supplier involved in multiple flagged cases
  2. User risk       — same user performing steps in multiple flagged cases
  3. Time clustering — multiple flagged cases opened within a short window
                       (possible coordinated attack burst)

Outputs two DataFrames (supplier_risk, user_risk) and annotates each
flagged case with a cross_case_risk flag.
"""

import pandas as pd
from datetime import timedelta

SUPPLIER_FLAG_THRESHOLD = 2   # flag supplier if involved in >= N flagged cases
USER_FLAG_THRESHOLD     = 2   # flag user if appears in >= N flagged cases
CLUSTER_WINDOW_HOURS    = 72  # cases starting within this window = a cluster


def supplier_risk(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate flagged cases by supplier.
    Returns a DataFrame sorted by flagged_cases descending.
    """
    flagged = results_df[results_df["flagged"] == True].copy()

    if "supplier_id" not in flagged.columns:
        return pd.DataFrame(columns=["supplier_id", "flagged_cases",
                                     "attack_types", "risk_flag"])

    grouped = (
        flagged.groupby("supplier_id")
        .agg(
            flagged_cases=("case_id", "count"),
            attack_types=("matched_attack", lambda x: sorted(set(x))),
        )
        .reset_index()
        .sort_values("flagged_cases", ascending=False)
    )
    grouped["risk_flag"] = grouped["flagged_cases"] >= SUPPLIER_FLAG_THRESHOLD
    return grouped


def user_risk(results_df: pd.DataFrame, full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate flagged cases by the users who appeared in them.
    full_df provides the event-level user column for cases that were flagged.
    Returns a DataFrame sorted by flagged_cases descending.
    """
    flagged_ids = set(results_df[results_df["flagged"] == True]["case_id"])

    user_col = "org:resource" if "org:resource" in full_df.columns else "user"
    case_col = "case:concept:name" if "case:concept:name" in full_df.columns else "case_id"

    involved = full_df[full_df[case_col].isin(flagged_ids)].copy()

    if user_col not in involved.columns:
        return pd.DataFrame(columns=["user", "flagged_cases", "risk_flag"])

    grouped = (
        involved.groupby(user_col)[case_col]
        .nunique()
        .reset_index()
        .rename(columns={user_col: "user", case_col: "flagged_cases"})
        .sort_values("flagged_cases", ascending=False)
    )
    grouped["risk_flag"] = grouped["flagged_cases"] >= USER_FLAG_THRESHOLD
    return grouped


def temporal_clusters(results_df: pd.DataFrame, full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify bursts: groups of flagged cases whose first event falls within
    CLUSTER_WINDOW_HOURS of each other.
    Returns a DataFrame with one row per cluster.
    """
    flagged_ids = set(results_df[results_df["flagged"] == True]["case_id"])
    case_col    = "case:concept:name" if "case:concept:name" in full_df.columns else "case_id"
    ts_col      = "time:timestamp"    if "time:timestamp"    in full_df.columns else "timestamp"

    case_starts = (
        full_df[full_df[case_col].isin(flagged_ids)]
        .groupby(case_col)[ts_col]
        .min()
        .reset_index()
        .rename(columns={case_col: "case_id", ts_col: "start_time"})
        .sort_values("start_time")
    )
    case_starts["start_time"] = pd.to_datetime(case_starts["start_time"])

    # Slide a window: each case anchors a window; count how many other flagged
    # cases start within CLUSTER_WINDOW_HOURS after it.
    window = timedelta(hours=CLUSTER_WINDOW_HOURS)
    clusters = []
    used = set()

    for _, anchor in case_starts.iterrows():
        if anchor["case_id"] in used:
            continue
        in_window = case_starts[
            (case_starts["start_time"] >= anchor["start_time"]) &
            (case_starts["start_time"] <= anchor["start_time"] + window)
        ]
        if len(in_window) >= 2:
            member_ids = list(in_window["case_id"])
            clusters.append({
                "cluster_start":  anchor["start_time"].isoformat(),
                "cluster_size":   len(in_window),
                "case_ids":       member_ids,
            })
            used.update(member_ids)

    return pd.DataFrame(clusters) if clusters else pd.DataFrame(
        columns=["cluster_start", "cluster_size", "case_ids"]
    )


def run(results_df: pd.DataFrame, full_df: pd.DataFrame) -> dict:
    """
    Run all three cross-case analyses and return a results dict.
    Also saves supplier_risk.csv and user_risk.csv to data/.
    """
    sup  = supplier_risk(results_df)
    usr  = user_risk(results_df, full_df)
    clus = temporal_clusters(results_df, full_df)

    sup.to_csv("data/supplier_risk.csv",  index=False)
    usr.to_csv("data/user_risk.csv",      index=False)

    return {
        "supplier_risk":      sup,
        "user_risk":          usr,
        "temporal_clusters":  clus,
    }


if __name__ == "__main__":
    import pandas as pd
    from src.preprocess import load_and_format, split_log

    results  = pd.read_csv("data/results.csv")
    df       = load_and_format("data/supply_chain_log.csv")
    _, full_df = split_log(df)

    output = run(results, full_df)

    sup  = output["supplier_risk"]
    usr  = output["user_risk"]
    clus = output["temporal_clusters"]

    print(f"{'='*55}")
    print(f"  CROSS-CASE CORRELATION RESULTS")
    print(f"{'='*55}")

    print(f"\n  Supplier Risk (threshold ≥ {SUPPLIER_FLAG_THRESHOLD} flagged cases):")
    risky_sup = sup[sup["risk_flag"]]
    if risky_sup.empty:
        print("  None above threshold")
    else:
        print(risky_sup[["supplier_id", "flagged_cases", "attack_types"]].to_string(index=False))

    print(f"\n  User Risk (threshold ≥ {USER_FLAG_THRESHOLD} flagged cases):")
    risky_usr = usr[usr["risk_flag"]]
    print(risky_usr[["user", "flagged_cases"]].to_string(index=False))

    print(f"\n  Temporal Clusters (within {CLUSTER_WINDOW_HOURS}h window):")
    if clus.empty:
        print("  No clusters detected")
    else:
        for _, row in clus.iterrows():
            print(f"  {row['cluster_start'][:10]}  size={row['cluster_size']}")

    print(f"\n  Saved → data/supplier_risk.csv")
    print(f"  Saved → data/user_risk.csv")
