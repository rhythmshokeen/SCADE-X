import ast
import pandas as pd

NORMAL_SEQUENCE = [
    "Create Purchase Requisition",
    "Manager Approval",
    "Send RFQ to Supplier",
    "Receive Supplier Quote",
    "Create Purchase Order",
    "Goods Receipt",
    "Invoice Verification",
    "Payment Release",
]


def _skipped_acts(activated_acts_raw) -> list[str]:
    """
    Infer which normal activities were absent from the trace by comparing
    the activated transitions to the known normal sequence.
    """
    if isinstance(activated_acts_raw, str):
        try:
            activated = ast.literal_eval(activated_acts_raw)
        except Exception:
            activated = []
    else:
        activated = list(activated_acts_raw or [])

    activated_set = set(activated)
    return [act for act in NORMAL_SEQUENCE if act not in activated_set]


# Each signature defines which combination of perspective signals identifies the attack.
# Every field is optional — a case is scored against all signatures and the best match wins.
SIGNATURES = {
    "payment_fraud": {
        "description": "Payment released before Goods Receipt or Invoice Verification",
        "risk_level": "CRITICAL",
        "recommended_action": (
            "Freeze payment immediately. Audit approver account for compromise. "
            "Verify goods were actually received before releasing any further payments."
        ),
        # CF signals
        "missing_acts_any": ["Goods Receipt", "Invoice Verification"],
        # Time signals
        "requires_fast_steps": True,
    },
    "approval_bypass": {
        "description": "Manager Approval step was skipped — procurement control bypassed",
        "risk_level": "HIGH",
        "recommended_action": (
            "Reverse transaction if possible. Investigate whether approver credentials "
            "were compromised or if the requester has elevated system permissions."
        ),
        "missing_acts_any": ["Manager Approval"],
        "requires_wrong_role": True,
    },
    "duplicate_payment": {
        "description": "Payment Release occurred more than once against the same purchase order",
        "risk_level": "CRITICAL",
        "recommended_action": (
            "Halt all pending payments for this supplier. Check for duplicate invoices "
            "and audit the accounts payable team. Recover the overpaid amount."
        ),
        "requires_duplicate_payment": True,
        "requires_amount_drift": True,
    },
    "unauthorized_supplier": {
        "description": "RFQ process bypassed — order placed without competitive bidding",
        "risk_level": "HIGH",
        "recommended_action": (
            "Verify supplier is on the approved vendor list. Request justification for "
            "skipping the RFQ process. Escalate to procurement compliance team."
        ),
        "missing_acts_any": ["Send RFQ to Supplier", "Receive Supplier Quote"],
    },
    "credential_compromise": {
        "description": "Critical procurement step performed from a compromised or suspicious account",
        "risk_level": "CRITICAL",
        "recommended_action": (
            "Immediately revoke session tokens for the involved user. Reset credentials "
            "and review all approvals made in the past 48 hours. Engage your SOC team "
            "for forensic investigation."
        ),
        "requires_security_flag": True,
    },
}


def _match_score(row: pd.Series, sig: dict, skipped: list[str]) -> int:
    """
    Count how many signals in a signature are satisfied by this case.
    Higher score = stronger match.
    skipped — list of normal activities absent from the case trace.
    """
    score = 0

    # Control-flow: check which normal steps were skipped
    if "missing_acts_any" in sig:
        if any(act in skipped for act in sig["missing_acts_any"]):
            score += 2   # CF match carries double weight

    # Time signal
    if sig.get("requires_fast_steps") and row.get("n_fast_steps", 0) > 0:
        score += 1

    # Resource signal
    if sig.get("requires_wrong_role") and row.get("wrong_role_count", 0) > 0:
        score += 1

    # Amount signals
    if sig.get("requires_duplicate_payment") and row.get("duplicate_payment", False):
        score += 2
    if sig.get("requires_amount_drift") and row.get("amount_drift_pct", 0) > 15:
        score += 1

    # Security context signal
    if sig.get("requires_security_flag") and row.get("security_events", 0) > 0:
        score += 3

    return score


def map_attacks(fused_df: pd.DataFrame) -> pd.DataFrame:
    """
    For every flagged case, determine the best-matching attack pattern.
    Appends matched_attack, confidence, risk_level, description, and
    recommended_action columns to the DataFrame.
    """
    matched_attacks  = []
    confidences      = []
    risk_levels      = []
    descriptions     = []
    actions          = []

    for _, row in fused_df.iterrows():
        if not row.get("flagged", False):
            matched_attacks.append("none")
            confidences.append("—")
            risk_levels.append("—")
            descriptions.append("—")
            actions.append("—")
            continue

        skipped = _skipped_acts(row.get("activated_acts", []))
        scores = {
            name: _match_score(row, sig, skipped)
            for name, sig in SIGNATURES.items()
        }

        best_name  = max(scores, key=scores.get)
        best_score = scores[best_name]

        if best_score == 0:
            matched_attacks.append("unknown_anomaly")
            confidences.append("LOW")
            risk_levels.append("MEDIUM")
            descriptions.append("Deviation detected but pattern not recognised")
            actions.append("Manual investigation required")
        else:
            # Confidence: LOW/MEDIUM/HIGH based on signal count
            confidence = "HIGH" if best_score >= 3 else ("MEDIUM" if best_score == 2 else "LOW")
            sig = SIGNATURES[best_name]
            matched_attacks.append(best_name)
            confidences.append(confidence)
            risk_levels.append(sig["risk_level"])
            descriptions.append(sig["description"])
            actions.append(sig["recommended_action"])

    out = fused_df.copy()
    out["matched_attack"]      = matched_attacks
    out["confidence"]          = confidences
    out["risk_level"]          = risk_levels
    out["attack_description"]  = descriptions
    out["recommended_action"]  = actions
    return out


if __name__ == "__main__":
    import pandas as pd

    fused = pd.read_csv("data/results.csv")
    result = map_attacks(fused)
    result.to_csv("data/results.csv", index=False)

    flagged = result[result["flagged"]]
    print(f"Flagged cases : {len(flagged)}")
    print(f"\nAttack mapping accuracy (matched vs planted):")

    for attack in ["payment_fraud", "approval_bypass", "duplicate_payment", "unauthorized_supplier"]:
        subset = flagged[flagged["attack_type"] == attack]
        correct = (subset["matched_attack"] == attack).sum()
        print(f"  {attack:<25} {correct}/{len(subset)} correctly mapped")

    print(f"\nSample output:")
    cols = ["case_id", "composite_score", "matched_attack", "confidence", "risk_level"]
    print(flagged[cols].head(8).to_string(index=False))
