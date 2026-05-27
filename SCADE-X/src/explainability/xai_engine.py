"""
SCADE-X Explainability (XAI) Engine
===================================
Main orchestration script for the XAI layer. Consumes all intelligence outputs,
generates deep explanations, produces case reports, and outputs the final
explanations dataset.
"""
import pandas as pd
from pathlib import Path
import logging

from src.explainability.root_cause_engine import estimate_root_cause
from src.explainability.action_engine import explain_action
from src.explainability.explanation_builder import (
    build_astra_explanation,
    build_scade_explanation,
    build_resilience_explanation,
    build_confidence_explanation,
    build_forensic_summary
)
from src.explainability.case_report_generator import CaseReportGenerator

logger = logging.getLogger("SCADE-X-XAI")

class XAIEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        
        # Inputs
        self.intel_path = self.base_dir / "data" / "intermediate" / "unified_case_intelligence.csv"
        self.resil_path = self.base_dir / "data" / "processed" / "resilience_intelligence.csv"
        self.final_path = self.base_dir / "data" / "processed" / "scadex_final_intelligence.csv"
        
        # Outputs
        self.exp_csv_path = self.base_dir / "data" / "processed" / "scadex_explanations.csv"
        self.reports_dir = self.base_dir / "outputs" / "reports"
        
        self.report_generator = CaseReportGenerator(self.reports_dir)

    def execute(self) -> pd.DataFrame:
        logger.info("Initializing XAI Engine...")
        
        if not all(p.exists() for p in [self.intel_path, self.resil_path, self.final_path]):
            logger.error("Required intelligence outputs are missing. Cannot generate explanations.")
            return pd.DataFrame()
            
        logger.info("Loading intelligence datasets...")
        intel_df = pd.read_csv(self.intel_path)
        resil_df = pd.read_csv(self.resil_path)
        final_df = pd.read_csv(self.final_path)
        
        # Merge everything into a massive unified dataframe for the explainer
        df = pd.merge(intel_df, resil_df, on="case_id", how="inner")
        df = pd.merge(df, final_df, on="case_id", how="inner")
        
        explanations = []
        logger.info("Generating forensic case explanations...")
        
        for _, row in df.iterrows():
            case_id = row["case_id"]
            
            # Root Cause
            rc = estimate_root_cause(row)
            
            # Action Explanation
            action_exp = explain_action(row.get("recommended_action", "MONITOR"), row)
            
            # Subsystem Explanations
            astra_exp = build_astra_explanation(row)
            scade_exp = build_scade_explanation(row)
            resil_exp = build_resilience_explanation(row)
            conf_exp = build_confidence_explanation(row)
            
            # Summary
            summary = build_forensic_summary(
                rc["primary_cause"], 
                row.get("threat_severity", "LOW"), 
                row.get("recommended_action", "MONITOR")
            )
            
            payload = {
                "case_id": case_id,
                "threat_severity": row.get("threat_severity", "LOW"),
                "escalation_priority": row.get("escalation_priority", "NONE"),
                "recommended_action": row.get("recommended_action", "MONITOR"),
                "root_cause": rc["primary_cause"],
                "secondary_causes": rc["secondary_causes"],
                "behavioral_explanation": astra_exp,
                "process_explanation": scade_exp,
                "security_explanation": "Security Context Engine evaluated." if pd.notna(row.get("security_score")) else "No security context provided.",
                "resilience_explanation": resil_exp,
                "recommended_action_reason": action_exp,
                "confidence_reason": conf_exp,
                "forensic_summary": summary
            }
            
            explanations.append(payload)
            
            # Optionally only generate detailed markdown/json reports for HIGH/CRITICAL cases
            # to save disk space, but the instructions implied 'every case'.
            # If the dataset is 10,000 cases, generating 10,000 JSON and MD files is 20,000 files.
            # We will generate it for cases that are flagged for escalation or anomaly.
            if row.get("escalation_priority", "NONE") != "NONE":
                self.report_generator.generate_report(case_id, payload)
                
        # Save aggregated CSV
        exp_df = pd.DataFrame(explanations)
        
        # Flatten lists for CSV
        exp_df["secondary_causes"] = exp_df["secondary_causes"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
        self.exp_csv_path.parent.mkdir(parents=True, exist_ok=True)
        exp_df.to_csv(self.exp_csv_path, index=False)
        logger.info(f"Generated explanations saved to {self.exp_csv_path}")
        logger.info(f"Detailed forensic reports saved to {self.reports_dir}")
        return exp_df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = XAIEngine(Path("."))
    engine.execute()
