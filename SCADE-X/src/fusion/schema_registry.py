"""
SCADE-X Schema Registry
=======================
Defines the canonical case-level intelligence schema.
Establishes datatype rules, subsystem mappings, and normalization semantics.
"""
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class CanonicalField:
    name: str
    dtype: str
    required: bool
    source_subsystem: str
    source_column: str
    description: str
    normalization_logic: str = "direct"  # direct, scale_0_1, invert, etc.

class SchemaRegistry:
    """Registry holding definitions for the unified intelligence DataFrame."""
    
    FIELDS = [
        CanonicalField("case_id", "str", True, "both", "case_id", "Primary unique identifier for a procurement trace"),
        
        # ASTRA Outputs
        CanonicalField("astra_risk_score", "float", False, "astra", "risk_score", "Weighted composite risk score", "scale_0_1"),
        CanonicalField("behavioral_score", "float", False, "astra", "behavior_scaled", "Transformer sequential anomaly score", "direct"),
        CanonicalField("iforest_score", "float", False, "astra", "iforest_scaled", "Statistical anomaly score", "direct"),
        CanonicalField("graph_score", "float", False, "astra", "supplier_scaled", "Supplier graph centrality risk", "direct"),
        CanonicalField("astra_predicted_anomaly", "bool", False, "astra", "predicted_anomaly", "ASTRA binary threshold flag", "direct"),
        
        # SCADE Outputs
        CanonicalField("scade_composite_score", "float", False, "scade", "composite_score", "Minimum-score composite conformance", "direct"),
        CanonicalField("cf_score", "float", False, "scade", "cf_score", "Control flow Token-Based Replay fitness", "direct"),
        CanonicalField("time_score", "float", False, "scade", "time_score", "Temporal baseline conformance", "direct"),
        CanonicalField("resource_score", "float", False, "scade", "resource_score", "Role and SOD conformance", "direct"),
        CanonicalField("amount_score", "float", False, "scade", "amount_score", "Amount drift tolerance score", "direct"),
        CanonicalField("security_score", "float", False, "scade", "security_score", "SIEM correlation penalty score", "direct"),
        CanonicalField("scade_flagged", "bool", False, "scade", "flagged", "SCADE minimum threshold flag", "direct"),
        
        # Metadata / Explanations
        CanonicalField("attack_type", "str", False, "scade", "attack_type", "Signature matched fraud category", "direct"),
        CanonicalField("is_ground_truth_anomaly", "bool", False, "scade", "is_anomaly", "Ground truth label (if available)", "direct")
    ]
    
    @classmethod
    def get_astra_mappings(cls) -> Dict[str, str]:
        return {f.source_column: f.name for f in cls.FIELDS if f.source_subsystem in ("astra", "both")}
        
    @classmethod
    def get_scade_mappings(cls) -> Dict[str, str]:
        return {f.source_column: f.name for f in cls.FIELDS if f.source_subsystem in ("scade", "both")}
        
    @classmethod
    def get_canonical_columns(cls) -> List[str]:
        return [f.name for f in cls.FIELDS]
        
    @classmethod
    def get_required_columns(cls) -> List[str]:
        return [f.name for f in cls.FIELDS if f.required]
