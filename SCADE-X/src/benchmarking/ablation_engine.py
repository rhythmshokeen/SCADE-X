"""
SCADE-X Ablation Engine
=======================
Measures the contribution of individual components by simulating
their removal from the fusion pipeline. Now includes resilience-specific
ablations (TTR/TTS, graph propagation, bottleneck detection).
"""
import pandas as pd
from typing import Dict, Any
from src.benchmarking.metrics_engine import compute_classification_metrics
from pathlib import Path


class AblationEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.intel_path = self.base_dir / "data" / "intermediate" / "unified_case_intelligence.csv"
        self.resil_path = self.base_dir / "data" / "processed" / "resilience_intelligence.csv"

    def _run_fusion(self, df: pd.DataFrame) -> pd.Series:
        """Runs the Hybrid Risk-Aware fusion math with current column values."""
        scores = []
        for _, row in df.iterrows():
            a_risk = row.get("astra_risk_score", 0.0)
            s_comp = row.get("scade_composite_score", 1.0)
            r_vuln = row.get("systemic_vulnerability", 0.0)
            prop = row.get("propagated_risk", 0.0)
            gap = row.get("resilience_gap", 0.0)

            # Handle NaNs
            a_risk = 0.0 if pd.isna(a_risk) else a_risk
            s_comp = 1.0 if pd.isna(s_comp) else s_comp
            r_vuln = 0.0 if pd.isna(r_vuln) else r_vuln
            prop = 0.0 if pd.isna(prop) else prop
            gap = 0.0 if pd.isna(gap) else gap

            s_risk = 1.0 - s_comp
            base_risk = max(s_risk, a_risk) * 0.7 + ((s_risk + a_risk) / 2.0) * 0.3
            amplification = 1.0 + (0.15 * r_vuln) + (0.10 * prop) + (0.10 * gap)
            scores.append(min(1.0, max(0.0, base_risk * amplification)))
        return pd.Series(scores, index=df.index)

    def execute(self) -> pd.DataFrame:
        if not self.intel_path.exists() or not self.resil_path.exists():
            return pd.DataFrame()

        intel_df = pd.read_csv(self.intel_path)
        resil_df = pd.read_csv(self.resil_path)
        df = pd.merge(intel_df, resil_df, on="case_id", how="inner")

        y_true = df.get("is_ground_truth_anomaly", pd.Series([0] * len(df))).fillna(0).astype(int)

        experiments = {
            "SCADE-X full": {},
            "Without ASTRA": {"astra_risk_score": 0.0},
            "Without SCADE": {"scade_composite_score": 1.0},
            "Without resilience (vulnerability)": {"systemic_vulnerability": 0.0},
            "Without graph propagation": {"propagated_risk": 0.0},
            "Without TTR/TTS (gap)": {"resilience_gap": 0.0},
            "Without graph + TTR/TTS": {"propagated_risk": 0.0, "resilience_gap": 0.0, "systemic_vulnerability": 0.0},
        }

        results = []
        for name, masks in experiments.items():
            df_copy = df.copy()
            for col, val in masks.items():
                if col in df_copy.columns:
                    df_copy[col] = val
            y_prob = self._run_fusion(df_copy)
            metrics = compute_classification_metrics(y_true, y_prob, threshold=0.65)
            results.append({"Configuration": name, **metrics})

        return pd.DataFrame(results)
