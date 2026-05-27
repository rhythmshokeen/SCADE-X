"""
SCADE-X Explanation Builder
===========================
Generates multi-layer forensic text explanations for ASTRA, SCADE,
Resilience (including TTR/TTS and graph propagation), and Final Fusion.
"""
from typing import Dict, Any
import math


def _s(val, default=0.0) -> float:
    if val is None:
        return default
    try:
        v = float(val)
        return v if not math.isnan(v) else default
    except (TypeError, ValueError):
        return default


def build_astra_explanation(row: Dict[str, Any]) -> str:
    b_score = _s(row.get("behavioral_score"))
    i_score = _s(row.get("iforest_score"))
    g_score = _s(row.get("graph_score"))

    exp = []
    if b_score > 0.7:
        exp.append(f"Transformer sequence analysis detected highly abnormal latent behavior (Score: {b_score:.2f}).")
    elif b_score > 0.4:
        exp.append(f"Moderate behavioural anomaly detected by transformer (Score: {b_score:.2f}).")
    if i_score > 0.7:
        exp.append(f"Isolation Forest flagged extreme statistical feature deviations (Score: {i_score:.2f}).")
    if g_score > 0.7:
        exp.append(f"Supply chain graph intelligence reveals risky topological positioning (Score: {g_score:.2f}).")

    if not exp:
        return "ASTRA detected normal or minor behavioral deviations."
    return " ".join(exp)


def build_scade_explanation(row: Dict[str, Any]) -> str:
    cf_score = _s(row.get("cf_score"), 1.0)
    time_score = _s(row.get("time_score"), 1.0)
    res_score = _s(row.get("resource_score"), 1.0)
    amt_score = _s(row.get("amount_score"), 1.0)

    exp = []
    if cf_score < 0.875:
        exp.append(f"Control Flow Replay failed (Fitness: {cf_score:.2f}), indicating skipped or extra steps.")
    if time_score < 0.875:
        exp.append(f"Temporal baseline violated (Score: {time_score:.2f}), indicating rushed or severely delayed execution.")
    if res_score < 0.875:
        exp.append(f"Resource compliance failed (Score: {res_score:.2f}), indicating wrong roles or SOD violations.")
    if amt_score < 0.875:
        exp.append(f"Amount drift detected (Score: {amt_score:.2f}), indicating financial discrepancy.")

    if not exp:
        return "SCADE detected standard process conformance."
    return " ".join(exp)


def build_resilience_explanation(row: Dict[str, Any]) -> str:
    vuln = _s(row.get("systemic_vulnerability"))
    prop = _s(row.get("propagated_risk"))
    dep = _s(row.get("dependency_risk", row.get("supplier_dependency_risk")))
    ttr = _s(row.get("ttr"))
    tts = _s(row.get("tts"), 1.0)
    gap = _s(row.get("resilience_gap"))
    bottleneck = _s(row.get("bottleneck_score"))

    parts = [
        f"Systemic Vulnerability: {vuln:.2f}.",
        f"Cascading propagation risk: {prop:.2f}.",
        f"Supplier dependency: {dep:.2f}.",
    ]

    if ttr > 0 or tts < 1.0:
        parts.append(f"TTR={ttr:.2f}, TTS={tts:.2f}.")
        if gap > 0:
            parts.append(f"RESILIENCE GAP: {gap:.2f} — recovery exceeds survival window.")

    if bottleneck > 0.5:
        parts.append(f"Supplier is a structural bottleneck (Score: {bottleneck:.2f}).")

    return " ".join(parts)


def build_confidence_explanation(row: Dict[str, Any]) -> str:
    conf = _s(row.get("confidence_score"))
    if conf > 0.8:
        return f"High Confidence ({conf:.2f}): Strong alignment between ASTRA behavioral modeling and SCADE deterministic rules."
    elif conf > 0.5:
        return f"Moderate Confidence ({conf:.2f}): Partial signal agreement across subsystems."
    else:
        return f"Low Confidence ({conf:.2f}): Subsystems yielded conflicting anomaly signals. Proceed with caution."


def build_forensic_summary(root_cause: str, severity: str, action: str) -> str:
    return (
        f"This {severity} severity case is primarily driven by '{root_cause}'. "
        f"System recommends {action}."
    )
