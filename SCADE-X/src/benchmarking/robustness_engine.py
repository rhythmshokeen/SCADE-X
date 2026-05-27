"""
SCADE-X Robustness Engine
=========================
Evaluates performance degradation under data corruption, missing data,
and simulated subsystem failures.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any
from pathlib import Path
from src.benchmarking.metrics_engine import compute_classification_metrics

class RobustnessEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.intel_path = self.base_dir / "data" / "intermediate" / "unified_case_intelligence.csv"
        
    def _simulate_fusion(self, df: pd.DataFrame) -> pd.Series:
        fusion_scores = []
        for _, row in df.iterrows():
            a_risk = row.get("astra_risk_score", 0.0)
            s_comp = row.get("scade_composite_score", 1.0)
            s_risk = 1.0 - (s_comp if pd.notna(s_comp) else 1.0)
            a_risk = a_risk if pd.notna(a_risk) else 0.0
            
            base_risk = max(s_risk, a_risk) * 0.7 + ((s_risk + a_risk) / 2.0) * 0.3
            fusion_scores.append(base_risk)
        return pd.Series(fusion_scores, index=df.index)

    def execute(self) -> pd.DataFrame:
        if not self.intel_path.exists():
            return pd.DataFrame()
            
        df = pd.read_csv(self.intel_path)
        y_true = df.get("is_ground_truth_anomaly", pd.Series([0]*len(df))).fillna(0).astype(int)
        
        results = []
        
        # 1. Baseline
        base_prob = self._simulate_fusion(df)
        results.append({"Scenario": "Baseline (Clean Data)", **compute_classification_metrics(y_true, base_prob)})
        
        # 2. Subsystem Failure (ASTRA Drops Out)
        df_astra_fail = df.copy()
        df_astra_fail["astra_risk_score"] = np.nan
        prob_astra_fail = self._simulate_fusion(df_astra_fail)
        results.append({"Scenario": "ASTRA Subsystem Offline", **compute_classification_metrics(y_true, prob_astra_fail)})
        
        # 3. Missing Data (Random 30% sparsity on SCADE scores)
        df_sparse = df.copy()
        mask = np.random.rand(len(df)) < 0.3
        df_sparse.loc[mask, "scade_composite_score"] = np.nan
        prob_sparse = self._simulate_fusion(df_sparse)
        results.append({"Scenario": "30% Sparse Process Logs", **compute_classification_metrics(y_true, prob_sparse)})
        
        # 4. Noise Injection (Corrupted ASTRA signals)
        df_noisy = df.copy()
        noise = np.random.normal(0, 0.2, len(df))
        df_noisy["astra_risk_score"] = np.clip(df_noisy["astra_risk_score"] + noise, 0, 1)
        prob_noisy = self._simulate_fusion(df_noisy)
        results.append({"Scenario": "Noisy Behavioral Signals (+20%)", **compute_classification_metrics(y_true, prob_noisy)})
        
        return pd.DataFrame(results)
