# SCADE-X Benchmarking Methodology

This document outlines the evaluation framework designed to scientifically validate the SCADE-X platform against its isolated subsystems.

## 1. Evaluation Metrics

SCADE-X is evaluated using a dual-faceted approach:
1. **Machine Learning Integrity**: ROC-AUC, PR-AUC, F1-Score, False Positive Rate (FPR), and Calibration Loss. ROC-AUC is prioritized as it is threshold-agnostic.
2. **Business Resilience Integrity**: 
   - *Disruption Detection Quality*: Correlation between ground truth fraud and predicted disruption severity tier.
   - *Recovery Prioritization Quality*: Average precision of the Escalation SLA against actual anomaly states.

## 2. Ablation Setup

The `ablation_engine.py` quantifies the marginal contribution of individual intelligence layers by masking them at runtime and recomputing the Hybrid Risk-Aware fusion:
1. **Baseline**: SCADE-X Full
2. **Without ASTRA**: Simulates purely deterministic conformance checking.
3. **Without SCADE**: Simulates purely latent behavioral learning.
4. **Without Resilience**: Masks the systemic vulnerability amplifier.
5. **Without Graph Intelligence**: Masks topological centrality.

*Interpretation*: The drop in ROC-AUC relative to the baseline proves the strict mathematical utility of that specific layer.

## 3. Robustness Testing

The `robustness_engine.py` evaluates the system's ability to survive adversarial or broken data pipelines:
1. **Subsystem Offline**: Simulates PyTorch OOM or execution failure. ASTRA is forcefully masked out.
2. **30% Sparsity**: Randomly drops 30% of SCADE outputs to simulate incomplete SIEM or ERP logs.
3. **Noisy Signals**: Injects +20% Gaussian noise into the ASTRA behavioral vectors to simulate concept drift or adversarial evasion.

## 4. Statistical Interpretation

- SCADE-X is designed to minimize the **False Positive Avalanche** inherent in Minimum-Score fusion. We expect to see SCADE-X maintain SCADE's high Recall while significantly boosting Precision.
- If the robust fallback mechanisms function correctly, SCADE-X running with an offline ASTRA subsystem should perfectly match the performance of pure SCADE, suffering zero cascading execution failure.
