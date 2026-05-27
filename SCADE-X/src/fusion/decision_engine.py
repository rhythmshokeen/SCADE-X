"""
SCADE-X Decision Engine
=======================
Maps fused intelligence scores into actionable business outcomes:
Threat Severity, Recommended Actions, and Escalation Priorities.
"""
from src.fusion.fusion_models import ThreatSeverity, RecommendedAction, EscalationPriority

def determine_threat_severity(final_risk_score: float, resilience_score: float) -> ThreatSeverity:
    """
    Severity is high if risk is high OR resilience is extremely low (meaning even
    a medium risk anomaly could shatter the process).
    """
    vuln = 1.0 - resilience_score
    effective_threat = (0.7 * final_risk_score) + (0.3 * vuln)
    
    if effective_threat > 0.85:
        return ThreatSeverity.CRITICAL
    elif effective_threat > 0.65:
        return ThreatSeverity.HIGH
    elif effective_threat > 0.40:
        return ThreatSeverity.MEDIUM
    return ThreatSeverity.LOW

def determine_recommended_action(
    severity: ThreatSeverity,
    security_score: float,
    amount_score: float,
    graph_score: float,
    resource_score: float,
    resilience_mitigation: str = None,
    resilience_priority: str = None
) -> RecommendedAction:
    """
    Selects the most urgent prescriptive action based on resilience intelligence
    and specific dimension failure.
    
    If the Resilience Engine flags a P1/P2 recovery priority, that mitigation 
    strategy overrides standard isolated rules.
    """
    # 1. Resilience Override for urgent systemic threats
    if resilience_priority in ("P1_CRITICAL", "P2_URGENT") and resilience_mitigation:
        # Map string to Enum dynamically or fallback
        try:
            return RecommendedAction[resilience_mitigation.upper()]
        except KeyError:
            # If not in the Enum exactly, use SUPPLIER_ESCALATION as generic severe resilience action
            return RecommendedAction.SUPPLIER_ESCALATION

    # 2. Standard isolated logic
    if severity in (ThreatSeverity.LOW, ThreatSeverity.MEDIUM):
        return RecommendedAction.MONITOR
        
    sec_risk = 1.0 - (security_score if security_score is not None else 1.0)
    amt_risk = 1.0 - (amount_score if amount_score is not None else 1.0)
    res_risk = 1.0 - (resource_score if resource_score is not None else 1.0)
    grp_risk = graph_score if graph_score is not None else 0.0
    
    # Identify the primary driver
    driver = max([
        (sec_risk, RecommendedAction.CREDENTIAL_RESET),
        (amt_risk, RecommendedAction.PAYMENT_FREEZE),
        (res_risk, RecommendedAction.PROCESS_ISOLATION),
        (grp_risk, RecommendedAction.SUPPLIER_ESCALATION)
    ], key=lambda x: x[0])
    
    # If the worst dimension is sufficiently bad, prescribe its action
    if driver[0] > 0.7:
        return driver[1]
        
    # Default fallback for severe anomalies lacking a clear single driver
    return RecommendedAction.AUDIT

def determine_escalation_priority(
    severity: ThreatSeverity, 
    confidence: float, 
    resilience_priority: str = None
) -> EscalationPriority:
    """
    Escalation depends on severity multiplied by our confidence in the signal,
    additionally boosted by critical resilience recovery requirements.
    """
    if resilience_priority == "P1_CRITICAL":
        return EscalationPriority.IMMEDIATE

    if severity == ThreatSeverity.CRITICAL and confidence > 0.75:
        return EscalationPriority.IMMEDIATE
    elif severity in (ThreatSeverity.CRITICAL, ThreatSeverity.HIGH) and confidence > 0.50:
        return EscalationPriority.URGENT
    elif severity == ThreatSeverity.MEDIUM or (severity == ThreatSeverity.HIGH and confidence <= 0.50):
        return EscalationPriority.STANDARD
    return EscalationPriority.NONE
