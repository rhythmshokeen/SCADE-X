"""
SCADE-X Intelligence Fusion Engine
==================================
Fuses normalized case intelligence and resilience intelligence into
a unified, final decision signal. Implements a Hybrid Risk-Aware
fusion strategy with real resilience amplification from TTR/TTS
and graph propagation metrics.
"""
import pandas as pd
import json
from pathlib import Path
import logging

from src.fusion.confidence_engine import compute_confidence
from src.fusion.decision_engine import (
    determine_threat_severity,
    determine_recommended_action,
    determine_escalation_priority,
)

logger = logging.getLogger("SCADE-X-IntelligenceFusion")


class IntelligenceFusionEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.intel_path = self.base_dir / "data" / "intermediate" / "unified_case_intelligence.csv"
        self.resil_path = self.base_dir / "data" / "processed" / "resilience_intelligence.csv"
        self.output_path = self.base_dir / "data" / "processed" / "scadex_final_intelligence.csv"
        self.strategy = "Hybrid_Risk_Aware_Fusion"

    def _compute_hybrid_risk(
        self, a_risk: float, s_comp: float, r_vuln: float, prop_risk: float, gap: float
    ) -> tuple[float, float]:
        """
        Hybrid Risk-Aware Fusion with real resilience signals.

        Base risk:   max-dominant non-linear blend of ASTRA and SCADE.
        Amplifier 1: systemic vulnerability (includes TTR/TTS fragility).
        Amplifier 2: graph propagation risk (cascading disruption).
        Amplifier 3: resilience gap penalty (TTR > TTS condition).

        R_final = min(1.0, R_base · (1 + 0.15·V_sys + 0.10·P_risk + 0.10·gap))
        """
        s_risk = 1.0 - s_comp
        base_risk = max(s_risk, a_risk) * 0.7 + ((s_risk + a_risk) / 2.0) * 0.3
        amplification = 1.0 + (0.15 * r_vuln) + (0.10 * prop_risk) + (0.10 * gap)
        return base_risk, min(1.0, max(0.0, base_risk * amplification))

    def _generate_explanations(self, row: pd.Series, final_risk: float, conf: float) -> str:
        exp = {
            "astra_signal": round(row.get("astra_risk_score", 0.0), 3),
            "scade_signal": round(1.0 - row.get("scade_composite_score", 1.0), 3),
            "systemic_vulnerability": round(row.get("systemic_vulnerability", 0.0), 3),
            "propagated_risk": round(row.get("propagated_risk", 0.0), 3),
            "resilience_gap": round(row.get("resilience_gap", 0.0), 3),
            "ttr": round(row.get("ttr", 0.0), 3),
            "tts": round(row.get("tts", 1.0), 3),
            "confidence_driver": "High Alignment" if conf > 0.7 else "Divergent Signals",
            "fusion_math": "Max-Dominant Non-Linear + Resilience + Propagation Amplification",
        }
        return json.dumps(exp)

    def execute_fusion(self) -> pd.DataFrame:
        logger.info("Loading unified intelligence and resilience outputs...")

        if not self.intel_path.exists() or not self.resil_path.exists():
            logger.error("Required upstream datasets are missing. Cannot fuse.")
            return pd.DataFrame()

        intel_df = pd.read_csv(self.intel_path)
        resil_df = pd.read_csv(self.resil_path)

        df = pd.merge(intel_df, resil_df, on="case_id", how="inner")

        records = []
        logger.info(f"Executing {self.strategy}...")

        for _, row in df.iterrows():
            case_id = row.get("case_id")

            a_risk = row.get("astra_risk_score", 0.0)
            s_comp = row.get("scade_composite_score", 1.0)
            r_vuln = row.get("systemic_vulnerability", 0.0)
            prop_risk = row.get("propagated_risk", 0.0)
            gap = row.get("resilience_gap", 0.0)
            resil = row.get("resilience_score", 1.0)

            # Safely handle NaNs
            a_risk = 0.0 if pd.isna(a_risk) else a_risk
            s_comp = 1.0 if pd.isna(s_comp) else s_comp
            r_vuln = 0.0 if pd.isna(r_vuln) else r_vuln
            prop_risk = 0.0 if pd.isna(prop_risk) else prop_risk
            gap = 0.0 if pd.isna(gap) else gap
            resil = 1.0 if pd.isna(resil) else resil

            base_risk, final_risk = self._compute_hybrid_risk(a_risk, s_comp, r_vuln, prop_risk, gap)
            conf = compute_confidence(a_risk, s_comp, r_vuln)

            resil_mitigation = row.get("mitigation_strategy")
            resil_priority = row.get("recovery_priority")

            severity = determine_threat_severity(final_risk, resil)
            action = determine_recommended_action(
                severity,
                row.get("security_score", 1.0),
                row.get("amount_score", 1.0),
                row.get("graph_score", 0.0),
                row.get("resource_score", 1.0),
                resilience_mitigation=resil_mitigation,
                resilience_priority=resil_priority
            )
            escalation = determine_escalation_priority(severity, conf, resilience_priority=resil_priority)

            resil_category = row.get("disruption_severity", "LOW")
            explain = self._generate_explanations(row, final_risk, conf)

            records.append({
                "case_id": case_id,
                "base_risk_score": round(base_risk, 4),
                "final_risk_score": round(final_risk, 4),
                "composite_intelligence_score": round(final_risk, 4),
                "confidence_score": round(conf, 4),
                "threat_severity": severity.value,
                "resilience_category": resil_category,
                "recommended_action": action.value,
                "escalation_priority": escalation.value,
                "fusion_strategy_used": self.strategy,
                "resilience_score": round(resil, 4),
                "systemic_vulnerability": round(r_vuln, 4),
                "propagated_risk": round(prop_risk, 4),
                "bottleneck_score": round(row.get("bottleneck_score", 0.0), 4),
                "dependency_risk": round(row.get("dependency_risk", 0.0), 4),
                "ttr": round(row.get("ttr", 0.0), 4),
                "tts": round(row.get("tts", 1.0), 4),
                "recovery_priority": resil_priority,
                "business_impact": round(row.get("business_impact", 0.0), 4),
                "continuity_risk": row.get("continuity_risk"),
                "mitigation_strategy": resil_mitigation,
                "mitigation_explanation": row.get("mitigation_explanation"),
                "contributing_signals": row.get("contributing_signals"),
                "explainability_signals": explain,
            })

        final_df = pd.DataFrame(records)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(self.output_path, index=False)
        logger.info(f"Final SCADE-X Intelligence saved to {self.output_path}")
        return final_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = IntelligenceFusionEngine(Path("."))
    engine.execute_fusion()
