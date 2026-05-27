"""
SCADE-X Confidence Engine
=========================
Computes the confidence score of the final anomaly prediction.
Confidence is derived from signal agreement, evidence strength,
and subsystem consistency.
"""

def compute_confidence(
    astra_risk: float,
    scade_composite: float,
    resilience_vuln: float
) -> float:
    """
    Computes a continuous confidence score [0, 1].
    
    1. Signal Agreement: If ASTRA says high risk and SCADE says high risk (low composite),
       agreement is high. If they disagree, confidence drops.
    2. Evidence Strength: If scores are pushed to extremes (>0.9 or <0.1), evidence is
       stronger than ambiguous mid-range scores (~0.5).
    """
    a_risk = astra_risk if astra_risk is not None else 0.5
    s_risk = (1.0 - scade_composite) if scade_composite is not None else 0.5
    r_vuln = resilience_vuln if resilience_vuln is not None else 0.5
    
    # 1. Signal Agreement (lower difference = higher agreement)
    agreement = 1.0 - abs(a_risk - s_risk)
    
    # 2. Evidence Strength (distance from the ambiguous 0.5 threshold)
    a_strength = abs(a_risk - 0.5) * 2.0  # Scales to [0, 1]
    s_strength = abs(s_risk - 0.5) * 2.0
    strength = (a_strength + s_strength) / 2.0
    
    # 3. Subsystem Consistency (does resilience align with raw anomalies?)
    avg_raw = (a_risk + s_risk) / 2.0
    consistency = 1.0 - abs(avg_raw - r_vuln)
    
    confidence = (0.5 * agreement) + (0.3 * strength) + (0.2 * consistency)
    return min(max(confidence, 0.0), 1.0)
