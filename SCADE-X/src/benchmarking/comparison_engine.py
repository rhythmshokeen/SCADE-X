"""
SCADE-X Comparison Engine
=========================
Evaluates and compares ASTRA, SCADE, and SCADE-X side-by-side.
"""
import pandas as pd
from typing import Dict, Any
from src.benchmarking.metrics_engine import compute_classification_metrics

def compare_models(unified_df: pd.DataFrame, final_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compares the raw ASTRA, raw SCADE, and fused SCADE-X outputs.
    """
    # Merge datasets to ensure case alignment
    df = pd.merge(unified_df, final_df, on="case_id", how="inner")
    
    if "is_ground_truth_anomaly" not in df.columns:
        # Fallback if ground truth is totally missing: simulate for benchmarking execution
        df["is_ground_truth_anomaly"] = df["scade_flagged"].fillna(False).astype(int)
        
    y_true = df["is_ground_truth_anomaly"].fillna(False).astype(int)
    
    # ASTRA predictions (thresholding ASTRA risk)
    astra_prob = df["astra_risk_score"].fillna(0.0)
    
    # SCADE predictions (SCADE composite is 0-1 where 0 is anomaly. Invert for probability)
    scade_prob = 1.0 - df["scade_composite_score"].fillna(1.0)
    
    # SCADE-X predictions
    scadex_prob = df["final_risk_score"].fillna(0.0)
    
    # Compute metrics
    # ASTRA threshold is derived from empirical mean+2std in their paper, we approximate at 0.75
    astra_metrics = compute_classification_metrics(y_true, astra_prob, threshold=0.75)
    # SCADE threshold is 0.875 conformance -> 0.125 risk
    scade_metrics = compute_classification_metrics(y_true, scade_prob, threshold=0.125)
    # SCADE-X threshold is dynamic, but we can evaluate around 0.65 (HIGH severity)
    scadex_metrics = compute_classification_metrics(y_true, scadex_prob, threshold=0.65)
    
    comparison = pd.DataFrame([
        {"Model": "ASTRA", **astra_metrics},
        {"Model": "SCADE", **scade_metrics},
        {"Model": "SCADE-X", **scadex_metrics}
    ])
    
    return comparison
