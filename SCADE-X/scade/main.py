import os
import time
import pandas as pd
import pm4py

from src.generate_data import generate_log
from src.preprocess import load_and_format, split_log, to_event_log
from src.ingest import (
    read_file, apply_column_map, apply_activity_map,
    format_for_pipeline, split_by_date, load_column_map,
    mark_synthetic, data_source,
)
from src.discover import discover_normal_model, save_model, load_model
from src.conformance.control_flow import score as cf_score
from src.conformance.time_perspective import fit as time_fit, save_time_model, load_time_model, score as time_score
from src.conformance.resource import fit as res_fit, save_resource_model, load_resource_model, score as res_score
from src.conformance.amount_delta import score as amt_score
from src.conformance.security_context import (
    fit as sec_fit, save_security_model, load_security_model, score as sec_score,
)
from src.conformance.fusion import fuse, detection_summary, ANOMALY_THRESHOLD
from src.attack_mapper import map_attacks
from src.cross_case import run as cross_case_run

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

RETRAIN               = not os.path.exists("models/normal_model.pkl")
UPLOAD_PATH           = "data/uploads/current.csv"
SECURITY_UPLOAD_PATH  = "data/uploads/security.csv"
COLUMN_MAP            = "config/column_map.json"


def _real_data_available() -> bool:
    return os.path.exists(UPLOAD_PATH) and os.path.exists(COLUMN_MAP)


def _load_security_log() -> pd.DataFrame | None:
    if os.path.exists(SECURITY_UPLOAD_PATH):
        try:
            return pd.read_csv(SECURITY_UPLOAD_PATH)
        except Exception:
            return None
    return None


def _step(label: str):
    print(f"\n  [{label}]", end=" ", flush=True)
    return time.time()


def _done(t0: float):
    print(f"done  ({time.time() - t0:.1f}s)")


def run(regenerate: bool = False, retrain: bool = RETRAIN):
    print("=" * 60)
    print("  SUPPLY CHAIN ANOMALY DETECTION ENGINE")
    print("  Multi-Perspective Process Conformance Analysis")
    print("=" * 60)

    # ── 1. Data ───────────────────────────────────────────────
    t = _step("1/7  Data")
    if _real_data_available():
        mapping = load_column_map(COLUMN_MAP)
        raw     = read_file(UPLOAD_PATH)
        raw     = apply_column_map(raw, mapping)
        raw     = apply_activity_map(raw)
        print(f"real data  {raw['case_id'].nunique()} cases", end=" ")
        use_real = True
    else:
        if regenerate or not os.path.exists("data/supply_chain_log.csv"):
            raw = generate_log(n_normal=200, n_anomalies=40)
            raw.to_csv("data/supply_chain_log.csv", index=False)
            print(f"demo data generated  {raw['case_id'].nunique()} cases", end=" ")
        else:
            raw = None
            print("demo data loaded from disk", end=" ")
        use_real = False
        mark_synthetic()
    _done(t)

    # ── 2. Preprocess ─────────────────────────────────────────
    t = _step("2/7  Preprocess")
    if use_real:
        df             = format_for_pipeline(raw)
        train_df, full_df = split_by_date(df, train_pct=0.70)
    else:
        df             = load_and_format("data/supply_chain_log.csv")
        train_df, full_df = split_log(df)
    train_log = to_event_log(train_df)
    full_log  = to_event_log(full_df)
    print(f"train={train_df['case:concept:name'].nunique()} cases  "
          f"full={full_df['case:concept:name'].nunique()} cases", end=" ")
    _done(t)

    # ── 3. Process discovery ──────────────────────────────────
    t = _step("3/7  Discover")
    if retrain:
        net, im, fm = discover_normal_model(train_log)
        save_model(net, im, fm)
        print("model trained", end=" ")
    else:
        net, im, fm = load_model()
        print("model loaded", end=" ")
    _done(t)

    # ── 4. Fit time + resource models ─────────────────────────
    t = _step("4/7  Fit perspectives")
    if retrain:
        time_model     = time_fit(train_df)
        resource_model = res_fit(train_df)
        save_time_model(time_model)
        save_resource_model(resource_model)
        print("time + resource models trained", end=" ")
    else:
        time_model     = load_time_model()
        resource_model = load_resource_model()
        print("time + resource models loaded", end=" ")
    _done(t)

    # ── 4.5. Security context (optional) ─────────────────────
    t = _step("4.5  Security")
    security_log = _load_security_log()
    if security_log is not None:
        if retrain:
            security_model = sec_fit(security_log)
            save_security_model(security_model)
        else:
            security_model = load_security_model()
        print(f"security log  {len(security_log)} events", end=" ")
    else:
        security_model = {}
        print("no security log — perspective disabled", end=" ")
    _done(t)

    # ── 5. Score all perspectives ─────────────────────────────
    t = _step("5/7  Score")
    cf_df       = cf_score(full_log, net, im, fm)
    time_df     = time_score(full_df, time_model)
    resource_df = res_score(full_df, resource_model)
    amount_df   = amt_score(full_df)
    if security_log is not None:
        security_df = sec_score(full_df, security_log, security_model)
        print("CF + time + resource + amount + security", end=" ")
    else:
        security_df = None
        print("CF + time + resource + amount", end=" ")
    _done(t)

    # ── 6. Fuse scores ────────────────────────────────────────
    t = _step("6/7  Fuse")
    extra_cols = [c for c in ("supplier_id", "org:resource") if c in full_df.columns]
    ground_truth = (
        full_df.groupby("case:concept:name")
        .first()[["attack_type", "is_anomaly"] + extra_cols]
        .reset_index()
    )
    fused = fuse(cf_df, time_df, resource_df, amount_df, ground_truth,
                 security_df=security_df)
    print(f"threshold={ANOMALY_THRESHOLD}  "
          f"flagged={fused['flagged'].sum()}/{len(fused)}", end=" ")
    _done(t)

    # ── 7. Map attack patterns ────────────────────────────────
    t = _step("7/7  Map attacks")
    result = map_attacks(fused)
    result.to_csv("data/results.csv", index=False)
    print(f"results saved → data/results.csv", end=" ")
    _done(t)

    # ── 7.5. Cross-case correlation ───────────────────────────
    t = _step("7.5  Cross-case")
    cross = cross_case_run(result, full_df)
    risky_suppliers = cross["supplier_risk"][cross["supplier_risk"]["risk_flag"]]
    risky_users     = cross["user_risk"][cross["user_risk"]["risk_flag"]]
    clusters        = cross["temporal_clusters"]
    print(f"{len(risky_suppliers)} flagged suppliers  "
          f"{len(risky_users)} flagged users  "
          f"{len(clusters)} time clusters", end=" ")
    _done(t)

    # ── Terminal report ───────────────────────────────────────
    detection_summary(result)
    _print_cross_case_summary(cross)
    _print_investigation_queue(result)

    return result


def _print_cross_case_summary(cross: dict):
    sup  = cross["supplier_risk"][cross["supplier_risk"]["risk_flag"]]
    usr  = cross["user_risk"][cross["user_risk"]["risk_flag"]]
    clus = cross["temporal_clusters"]

    print(f"\n{'─'*60}")
    print(f"  CROSS-CASE CORRELATION")
    print(f"{'─'*60}")

    if not sup.empty:
        print(f"  Suppliers involved in multiple flagged cases:")
        for _, r in sup.iterrows():
            attacks = ", ".join(r["attack_types"]) if isinstance(r["attack_types"], list) else r["attack_types"]
            print(f"    {r['supplier_id']:<12} {r['flagged_cases']} cases  [{attacks}]")

    if not usr.empty:
        print(f"  Users appearing in multiple flagged cases:")
        for _, r in usr.head(5).iterrows():
            print(f"    {r['user']:<12} {r['flagged_cases']} cases")

    if not clus.empty:
        print(f"  Time clusters (≥2 flagged cases within 72h):")
        for _, r in clus.iterrows():
            print(f"    {r['cluster_start'][:10]}  {r['cluster_size']} cases")


def _print_investigation_queue(result: pd.DataFrame):
    flagged = (
        result[result["flagged"]]
        .sort_values(["risk_level", "composite_score"])
    )

    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2}
    flagged = flagged.iloc[
        flagged["risk_level"].map(order).fillna(9).argsort()
    ]

    print(f"\n{'─'*60}")
    print(f"  INVESTIGATION QUEUE  ({len(flagged)} cases)")
    print(f"{'─'*60}")
    print(f"  {'CASE':<12} {'SCORE':>6}  {'RISK':<10} {'PATTERN':<25} {'CONF'}")
    print(f"  {'─'*56}")

    for _, row in flagged.iterrows():
        print(
            f"  {row['case_id']:<12} "
            f"{row['composite_score']:>6.3f}  "
            f"{row['risk_level']:<10} "
            f"{row['matched_attack']:<25} "
            f"{row['confidence']}"
        )

    print(f"{'─'*60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the SCADE pipeline")
    parser.add_argument("--regenerate", action="store_true",
                        help="Regenerate synthetic data even if CSV exists")
    parser.add_argument("--retrain", action="store_true",
                        help="Retrain process models even if saved models exist")
    args = parser.parse_args()

    run(regenerate=args.regenerate, retrain=args.retrain)
