"""
SCADE-X Fusion Models
=====================
Data structures, Enums, and foundational types for the final
Intelligence Fusion Engine.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class ThreatSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RecommendedAction(str, Enum):
    MONITOR = "MONITOR"
    AUDIT = "AUDIT"
    SUPPLIER_ESCALATION = "SUPPLIER_ESCALATION"
    PAYMENT_FREEZE = "PAYMENT_FREEZE"
    PROCESS_ISOLATION = "PROCESS_ISOLATION"
    CREDENTIAL_RESET = "CREDENTIAL_RESET"
    RESILIENCE_INTERVENTION = "RESILIENCE_INTERVENTION"

class EscalationPriority(str, Enum):
    NONE = "NONE"
    STANDARD = "STANDARD"
    URGENT = "URGENT"
    IMMEDIATE = "IMMEDIATE"

@dataclass
class FinalIntelligenceOutput:
    case_id: str
    final_risk_score: float
    composite_intelligence_score: float
    confidence_score: float
    threat_severity: str
    resilience_category: str
    recommended_action: str
    escalation_priority: str
    fusion_strategy_used: str
    explainability_signals: str  # JSON representation of contributing factors
