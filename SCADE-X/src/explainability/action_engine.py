"""
SCADE-X Action Recommendation Explainer
=======================================
Explains WHY a specific prescriptive action was recommended based
on underlying forensic drivers.
"""
from typing import Dict, Any

def explain_action(recommended_action: str, row: Dict[str, Any]) -> str:
    """
    Generates human-readable explanations for recommended actions.
    """
    if recommended_action == "MONITOR":
        return "Anomaly severity is low. The risk does not justify immediate intervention. Suggest adding to routine audit review."
        
    elif recommended_action == "CREDENTIAL_RESET":
        sec_risk = 1.0 - row.get("security_score", 1.0)
        return (f"Security signals indicated highly abnormal session context or potential credential "
                f"compromise (Security Penalty: {sec_risk:.2f}). Immediate password reset is required "
                f"to prevent further unauthorized access.")
                
    elif recommended_action == "PAYMENT_FREEZE":
        amt_risk = 1.0 - row.get("amount_score", 1.0)
        return (f"Amount delta engine detected a severe financial discrepancy or duplicate payment "
                f"release (Amount Penalty: {amt_risk:.2f}). Immediate financial freeze required to prevent capital leakage.")
                
    elif recommended_action == "PROCESS_ISOLATION":
        res_risk = 1.0 - row.get("resource_score", 1.0)
        return (f"Severe Segregation of Duties (SOD) or Role violation detected (Resource Penalty: {res_risk:.2f}). "
                f"The transaction workflow must be isolated pending HR and compliance review.")
                
    elif recommended_action == "SUPPLIER_ESCALATION":
        grp_risk = row.get("graph_score", 0.0)
        return (f"Topological analysis indicates this anomaly centers on a highly fragile or critical supplier "
                f"(Supplier Centrality Risk: {grp_risk:.2f}). Strategic procurement review recommended.")
                
    elif recommended_action == "AUDIT":
        return ("Composite anomalies across multiple domains indicate a complex procedural failure. "
                "Manual forensic audit is required to assess underlying business logic errors.")
                
    return f"Default intervention protocol triggered for action: {recommended_action}."
