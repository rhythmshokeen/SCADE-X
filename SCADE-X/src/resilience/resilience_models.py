"""
SCADE-X Resilience Models
=========================
Data structures and foundational mathematical components for the
Supply Chain Resilience Intelligence Layer.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import math


class DisruptionSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecoveryPriority(str, Enum):
    P4_ROUTINE = "P4_ROUTINE"
    P3_ELEVATED = "P3_ELEVATED"
    P2_URGENT = "P2_URGENT"
    P1_CRITICAL = "P1_CRITICAL"


def _safe(val) -> float:
    if val is None:
        return 0.0
    try:
        v = float(val)
        return v if not math.isnan(v) else 0.0
    except (TypeError, ValueError):
        return 0.0


def compute_operational_fragility(
    astra_risk: float,
    scade_composite: float,
    ttr_tts_fragility: float,
) -> float:
    """
    Operational fragility: how close a case is to structural failure.

    Integrates three independent signals:
    - ASTRA latent behavioural risk (higher = riskier)
    - SCADE deterministic conformance (lower = riskier, so we invert)
    - TTR/TTS fragility ratio (higher = recovery exceeds survival)

    Formula:
        F = 0.30·A_risk + 0.40·(1 - S_composite) + 0.30·TTR_TTS_fragility

    The TTR/TTS component elevates fragility when recovery time exceeds
    the survival window, making this a genuine resilience signal rather
    than just an anomaly re-weighting.
    """
    a_risk = _safe(astra_risk)
    s_risk = 1.0 - _safe(scade_composite)
    ttr_f = _safe(ttr_tts_fragility)

    return min(1.0, 0.30 * a_risk + 0.40 * s_risk + 0.30 * ttr_f)


def map_disruption_severity(
    fragility: float,
    num_perspectives_violated: int,
    resilience_gap: float,
) -> DisruptionSeverity:
    """
    Maps continuous fragility, violated perspective count, and the
    resilience gap into a categorical disruption intensity.

    The resilience_gap (TTR - TTS, clamped at 0) acts as an independent
    escalation trigger: even moderate fragility becomes CRITICAL if the
    system cannot recover in time.
    """
    gap = _safe(resilience_gap)

    if fragility > 0.85 or num_perspectives_violated >= 3 or gap > 0.3:
        return DisruptionSeverity.CRITICAL
    elif fragility > 0.65 or num_perspectives_violated == 2 or gap > 0.15:
        return DisruptionSeverity.HIGH
    elif fragility > 0.40 or num_perspectives_violated == 1 or gap > 0.05:
        return DisruptionSeverity.MEDIUM
    return DisruptionSeverity.LOW
