"""
SCADE-X Recovery Recommendation Engine
=======================================
Generates actionable, context-dependent supply chain resilience
recommendations based on TTR/TTS, propagation risk, supplier
criticality, and process conformance signals.

Every recommendation is accompanied by an explanation of WHY
it was selected, grounded in the input signals.
"""
from typing import Dict, Any
import math

# Priority tiers
PRIORITY_P1 = "P1_CRITICAL"
PRIORITY_P2 = "P2_URGENT"
PRIORITY_P3 = "P3_ELEVATED"
PRIORITY_P4 = "P4_ROUTINE"


def _safe(val, default=0.0) -> float:
    if val is None:
        return default
    try:
        v = float(val)
        return v if not math.isnan(v) else default
    except (TypeError, ValueError):
        return default


def recommend_mitigation(row: Dict[str, Any]) -> Dict[str, str]:
    """
    Selects the most appropriate mitigation strategy and generates
    an evidence-based recommendation explanation.

    Decision logic priority:
    1. resilience_gap > 0 + high propagation  → reroute_supplier
    2. security compromise                     → freeze_and_reset
    3. high financial drift                    → freeze_transaction
    4. high supplier criticality + bottleneck  → diversify_sourcing
    5. SOD / resource violations               → expedite_audit
    6. moderate anomaly only                   → monitor_only
    """
    gap = _safe(row.get("resilience_gap"), 0.0)
    prop = _safe(row.get("propagated_risk"), 0.0)
    bottleneck = _safe(row.get("bottleneck_score"), 0.0)
    sup_crit = _safe(row.get("supplier_criticality"), 0.0)
    sec_score = _safe(row.get("security_score"), 1.0)
    amt_score = _safe(row.get("amount_score"), 1.0)
    res_score = _safe(row.get("resource_score"), 1.0)
    ttr = _safe(row.get("ttr"), 0.0)
    tts = _safe(row.get("tts"), 1.0)

    # Rule 1: Resilience gap with high propagation → systemic rerouting
    if gap > 0.15 and prop > 0.3:
        return {
            "mitigation_strategy": "reroute_supplier",
            "recommended_action": "Reroute procurement to alternative supplier and initiate buffer replenishment",
            "resilience_priority": PRIORITY_P1,
            "continuity_risk": "HIGH",
            "explanation": (
                f"TTR ({ttr:.2f}) exceeds TTS ({tts:.2f}) by a gap of {gap:.2f}, "
                f"and propagated risk is {prop:.2f}. The supply chain cannot recover "
                f"before catastrophic impact. Immediate supplier rerouting is required."
            ),
        }

    # Rule 2: Active security compromise → credential reset + freeze
    sec_risk = 1.0 - sec_score
    if sec_risk > 0.5:
        return {
            "mitigation_strategy": "freeze_and_reset",
            "recommended_action": "Freeze transaction, reset credentials, and escalate to SIEM team",
            "resilience_priority": PRIORITY_P1,
            "continuity_risk": "HIGH",
            "explanation": (
                f"Security score is {sec_score:.2f} (risk: {sec_risk:.2f}), indicating "
                f"potential credential compromise or SIEM-correlated threat. "
                f"Immediate credential reset and transaction freeze required."
            ),
        }

    # Rule 3: Large financial drift → payment freeze
    amt_risk = 1.0 - amt_score
    if amt_risk > 0.5:
        return {
            "mitigation_strategy": "freeze_transaction",
            "recommended_action": "Freeze payment and initiate financial reconciliation audit",
            "resilience_priority": PRIORITY_P2,
            "continuity_risk": "MEDIUM",
            "explanation": (
                f"Amount conformance is {amt_score:.2f} (drift: {amt_risk:.2f}), "
                f"signalling duplicate payment or significant value deviation. "
                f"Payment freeze prevents further capital leakage."
            ),
        }

    # Rule 4: Critical bottleneck supplier → diversify sourcing
    if bottleneck > 0.5 and sup_crit > 0.3:
        return {
            "mitigation_strategy": "diversify_sourcing",
            "recommended_action": "Initiate secondary supplier qualification and increase safety inventory",
            "resilience_priority": PRIORITY_P2,
            "continuity_risk": "MEDIUM",
            "explanation": (
                f"Supplier bottleneck score is {bottleneck:.2f} with criticality {sup_crit:.2f}. "
                f"This supplier is a structural chokepoint in the supply chain graph. "
                f"Diversification reduces single-point-of-failure exposure."
            ),
        }

    # Rule 5: SOD / resource violations → expedite audit
    res_risk = 1.0 - res_score
    if res_risk > 0.3:
        return {
            "mitigation_strategy": "expedite_audit",
            "recommended_action": "Expedite compliance audit for role and segregation-of-duties violations",
            "resilience_priority": PRIORITY_P3,
            "continuity_risk": "LOW",
            "explanation": (
                f"Resource conformance is {res_score:.2f} (risk: {res_risk:.2f}), "
                f"indicating potential SOD violations. Compliance audit prevents "
                f"escalation to regulatory exposure."
            ),
        }

    # Rule 6: Default → monitor
    return {
        "mitigation_strategy": "monitor_only",
        "recommended_action": "Add to routine monitoring queue; no immediate intervention required",
        "resilience_priority": PRIORITY_P4,
        "continuity_risk": "NEGLIGIBLE",
        "explanation": (
            "No individual risk dimension exceeds actionable thresholds. "
            "The case is within acceptable operational variance."
        ),
    }
