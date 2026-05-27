"""
SCADE-X Root Cause Engine
=========================
Determines the primary and secondary causes of an anomalous case
by evaluating the normalized signals from ASTRA and SCADE.
"""
from typing import Dict, Any, List

def estimate_root_cause(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estimates primary_cause, secondary_cause, and contributing_signals.
    """
    causes = []
    
    # Extract failure signals (thresholds are illustrative/configurable)
    if row.get("cf_score", 1.0) < 0.875:
        causes.append(("Process Workflow Deviation (Skipped/Extra Steps)", 1.0 - row.get("cf_score", 1.0)))
    if row.get("resource_score", 1.0) < 0.875:
        causes.append(("Segregation of Duties / Role Violation", 1.0 - row.get("resource_score", 1.0)))
    if row.get("amount_score", 1.0) < 0.875:
        causes.append(("Financial Drift / Duplicate Payment", 1.0 - row.get("amount_score", 1.0)))
    if row.get("security_score", 1.0) < 0.875:
        causes.append(("SIEM Security Event / Credential Compromise", 1.0 - row.get("security_score", 1.0)))
    if row.get("behavioral_score", 0.0) > 0.8:
        causes.append(("Latent Behavioral Sequence Anomaly", row.get("behavioral_score", 0.0)))
    if row.get("graph_score", 0.0) > 0.8:
        causes.append(("Supplier Network Centrality Risk", row.get("graph_score", 0.0)))
        
    # Sort causes by severity magnitude (descending)
    causes.sort(key=lambda x: x[1], reverse=True)
    
    primary = causes[0][0] if len(causes) > 0 else "Normal Operational Variance"
    secondary = [c[0] for c in causes[1:3]] if len(causes) > 1 else []
    signals = [f"{c[0]} (Magnitude: {c[1]:.2f})" for c in causes]
    
    return {
        "primary_cause": primary,
        "secondary_causes": secondary,
        "contributing_signals": signals
    }
