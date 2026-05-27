"""
SCADE-X Metrics Engine
======================
Computes standard machine learning metrics and custom resilience-oriented
evaluation metrics for the SCADE-X platform.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix,
    brier_score_loss
)

def compute_classification_metrics(y_true: pd.Series, y_prob: pd.Series, threshold: float = 0.8) -> Dict[str, float]:
    """
    Computes standard ML classification metrics.
    """
    # Defensive handling for NaNs
    mask = y_true.notna() & y_prob.notna()
    y_true_clean = y_true[mask].astype(int)
    y_prob_clean = y_prob[mask]
    
    if len(np.unique(y_true_clean)) < 2:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "roc_auc": 0.0, "pr_auc": 0.0, "fpr": 0.0, "fnr": 0.0, "calibration": 0.0}

    y_pred = (y_prob_clean >= threshold).astype(int)
    
    tn, fp, fn, tp = confusion_matrix(y_true_clean, y_pred, labels=[0, 1]).ravel()
    
    metrics = {
        "accuracy": accuracy_score(y_true_clean, y_pred),
        "precision": precision_score(y_true_clean, y_pred, zero_division=0),
        "recall": recall_score(y_true_clean, y_pred, zero_division=0),
        "f1": f1_score(y_true_clean, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true_clean, y_prob_clean),
        "pr_auc": average_precision_score(y_true_clean, y_prob_clean),
        "fpr": fp / (fp + tn) if (fp + tn) > 0 else 0.0,
        "fnr": fn / (fn + tp) if (fn + tp) > 0 else 0.0,
        "calibration": brier_score_loss(y_true_clean, y_prob_clean)
    }
    return {k: round(v, 4) for k, v in metrics.items()}

def compute_resilience_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Computes custom resilience-oriented ranking and quality metrics.
    Assumes df contains ground truth 'is_ground_truth_anomaly' and resilience scores.
    """
    if "is_ground_truth_anomaly" not in df.columns or df["is_ground_truth_anomaly"].isna().all():
        return {}
        
    mask = df["is_ground_truth_anomaly"].notna()
    clean_df = df[mask].copy()
    y_true = clean_df["is_ground_truth_anomaly"].astype(int)
    
    # 1. Disruption Detection Quality (Correlation between true anomaly and disruption severity scalar)
    severity_map = {"LOW": 0.1, "MEDIUM": 0.4, "HIGH": 0.7, "CRITICAL": 1.0}
    clean_df["severity_scalar"] = clean_df["resilience_category"].map(severity_map).fillna(0.1)
    disruption_quality = roc_auc_score(y_true, clean_df["severity_scalar"]) if len(np.unique(y_true)) > 1 else 0.0
    
    # 2. Recovery Prioritization Quality (Are true anomalies ranked higher in SLA?)
    # Assuming we have escalation_priority or we can map it
    pri_map = {"NONE": 0, "STANDARD": 1, "URGENT": 2, "IMMEDIATE": 3}
    if "escalation_priority" in clean_df.columns:
        clean_df["pri_scalar"] = clean_df["escalation_priority"].map(pri_map).fillna(0)
        priority_quality = average_precision_score(y_true, clean_df["pri_scalar"]) if len(np.unique(y_true)) > 1 else 0.0
    else:
        priority_quality = 0.0
        
    return {
        "disruption_detection_quality": round(disruption_quality, 4),
        "recovery_prioritization_quality": round(priority_quality, 4)
    }
