import numpy as np
import pandas as pd

# A payment is flagged as drifted if it exceeds the PO amount by more than this fraction.
DRIFT_THRESHOLD = 0.15   # 15% tolerance for legitimate rounding/fees


def score(full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Score every case on the amount/data perspective.

    Checks:
      1. Amount drift — Payment Release amount deviates > DRIFT_THRESHOLD from
         the Create Purchase Order amount.
      2. Duplicate payments — Payment Release occurs more than once in a case,
         flagged regardless of amount.

    Returns one row per case:
      case_id           — case identifier
      amount_score      — 0–1 (1 = no amount anomalies)
      amount_drift_pct  — % difference between PO and final payment (0 if no PO found)
      duplicate_payment — True if Payment Release appears more than once
    """
    rows = []

    for case_id, group in full_df.groupby("case:concept:name"):
        group = group.sort_values("time:timestamp")

        po_rows = group[group["concept:name"] == "Create Purchase Order"]
        pr_rows = group[group["concept:name"] == "Payment Release"]

        duplicate_payment = len(pr_rows) > 1

        # Amount drift: compare PO amount to the last Payment Release amount
        drift_pct = 0.0
        if not po_rows.empty and not pr_rows.empty:
            po_amount = float(po_rows.iloc[0]["amount"])
            last_payment = float(pr_rows.iloc[-1]["amount"])

            if po_amount > 0:
                drift_pct = abs(last_payment - po_amount) / po_amount

        # Build score: each signal contributes independently
        penalties = []

        if duplicate_payment:
            penalties.append(1.0)       # hard penalty — duplicates are always wrong

        if drift_pct > DRIFT_THRESHOLD:
            # Scale penalty with how far over the threshold the drift is
            excess = drift_pct - DRIFT_THRESHOLD
            penalty = min(excess / 0.5, 1.0)   # caps at 1.0 when drift >= 65%
            penalties.append(round(penalty, 4))

        avg_penalty   = float(np.mean(penalties)) if penalties else 0.0
        amount_score  = round(max(0.0, 1.0 - avg_penalty), 4)

        rows.append({
            "case_id":           case_id,
            "amount_score":      amount_score,
            "amount_drift_pct":  round(drift_pct * 100, 2),
            "duplicate_payment": duplicate_payment,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    from src.preprocess import load_and_format, split_log

    df = load_and_format("data/supply_chain_log.csv")
    _, full_df = split_log(df)

    print("Scoring amount perspective...")
    results = score(full_df)

    print(f"Cases scored          : {len(results)}")
    print(f"Duplicate payments    : {results['duplicate_payment'].sum()}")
    print(f"Drift > threshold     : {(results['amount_drift_pct'] > DRIFT_THRESHOLD * 100).sum()}")
    print(f"Amount score < 1.0   : {(results['amount_score'] < 1.0).sum()}")
    print("\nFlagged cases:")
    flagged = results[results["amount_score"] < 1.0]
    print(flagged[["case_id","amount_score","amount_drift_pct","duplicate_payment"]].to_string(index=False))
