"""
SCADE-X TTR / TTS Engine
=========================
Computes Time To Recover (TTR) and Time To Survive (TTS) estimates
for each case, based on available subsystem signals.

Definitions
-----------
TTR (Time To Recover):
    Estimated time (in normalised units) for the organisation to fully
    remediate the disruption associated with this case. Driven by the
    complexity of the violations (SOD rework, forensic audit depth,
    payment reversal bureaucracy).

TTS (Time To Survive):
    Estimated time the supply chain can sustain normal operations
    before the disruption becomes catastrophic. Driven by supplier
    criticality and process conformance margins.

Key invariant:
    If TTR > TTS, the system cannot recover before catastrophic impact.
    This produces a positive `resilience_gap` which degrades the
    overall resilience score.

All values are normalised to [0, 1] where 1 represents maximum
duration/difficulty. The actual calendar mapping depends on
deployment context.
"""
import math


def estimate_ttr(
    resource_score: float,
    time_score: float,
    amount_score: float,
    iforest_score: float,
) -> float:
    """
    Estimate Time To Recover.

    Recovery is slow when:
    - SOD/role violations exist (resource_score low) → legal review
    - Temporal deviations are deep (time_score low) → audit trail reconstruction
    - Financial drift is large (amount_score low) → payment reversal complexity
    - Statistical anomaly is extreme (iforest_score high) → manual forensic review

    Formula:
        TTR = 0.35·(1-resource) + 0.25·(1-time) + 0.25·(1-amount) + 0.15·iforest

    Returns a value in [0, 1].
    """
    r = 1.0 - _safe(resource_score, 1.0)
    t = 1.0 - _safe(time_score, 1.0)
    a = 1.0 - _safe(amount_score, 1.0)
    i = _safe(iforest_score, 0.0)

    ttr = 0.35 * r + 0.25 * t + 0.25 * a + 0.15 * i
    return min(1.0, max(0.0, ttr))


def estimate_tts(
    supplier_criticality: float,
    cf_score: float,
    security_score: float,
) -> float:
    """
    Estimate Time To Survive.

    Survival window shrinks when:
    - The supplier is highly critical (high centrality) → no alternative
    - Control flow is severely broken (cf_score low) → process is dysfunctional
    - Security is compromised (security_score low) → active threat window

    Survival is modelled as an inverse: a high-criticality supplier with
    a broken process and active security compromise has near-zero TTS.

    Formula:
        raw = 1.0 - [0.40·criticality + 0.35·(1-cf) + 0.25·(1-security)]
        TTS = max(0.05, raw)   # floor at 0.05 to avoid division-by-zero

    A TTS of 1.0 means effectively infinite survival (no urgency).
    A TTS of 0.05 means catastrophic imminent failure.
    """
    c = _safe(supplier_criticality, 0.0)
    cf_risk = 1.0 - _safe(cf_score, 1.0)
    sec_risk = 1.0 - _safe(security_score, 1.0)

    raw = 1.0 - (0.40 * c + 0.35 * cf_risk + 0.25 * sec_risk)
    return max(0.05, min(1.0, raw))


def compute_resilience_gap(ttr: float, tts: float) -> float:
    """
    The resilience gap is the excess recovery time beyond the survival window.

        gap = max(0, TTR - TTS)

    A positive gap means the system cannot recover before catastrophic impact.
    """
    return max(0.0, ttr - tts)


def compute_ttr_tts_fragility(ttr: float, tts: float) -> float:
    """
    Computes a continuous fragility score from TTR/TTS ratio.

        fragility = TTR / (TTR + TTS)

    When TTR >> TTS: fragility → 1.0 (highly fragile)
    When TTR << TTS: fragility → 0.0 (resilient)
    When TTR == TTS: fragility = 0.5 (borderline)
    """
    denom = ttr + tts
    if denom < 1e-9:
        return 0.0
    return ttr / denom


def _safe(val, default=0.0) -> float:
    """Safely coerce a value to float, defaulting NaN/None to default."""
    if val is None:
        return default
    try:
        v = float(val)
        return v if not math.isnan(v) else default
    except (TypeError, ValueError):
        return default
