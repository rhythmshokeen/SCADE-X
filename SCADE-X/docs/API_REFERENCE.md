# SCADE-X API Reference

This document catalogs the core modules within the SCADE-X orchestration framework.

## `src/orchestration/scadex_pipeline.py`
**Class: `SCADEXUnifiedPipeline`**
- `execute()`: Master orchestration loop. Validates inputs, spawns ASTRA/SCADE subprocesses, triggers Schema Normalization, Resilience, Fusion, XAI, and Benchmarking sequentially.

## `src/fusion/schema_normalizer.py`
**Class: `SchemaNormalizer`**
- `normalize() -> pd.DataFrame`: Ingests `ASTRA/data/processed/fused_risk_scores.csv` and `SCADE/data/results.csv`. Performs outer join on `case_id`. Compresses unbound ASTRA variables into $[0, 1]$ bounds.

## `src/resilience/resilience_engine.py`
**Class: `ResilienceEngine`**
- `compute_resilience() -> pd.DataFrame`: Calculates `Operational Fragility`, `Disruption Severity`, `Supplier Dependency Risk`, and `Systemic Vulnerability`. Outputs `resilience_intelligence.csv`.

## `src/fusion/intelligence_fusion.py`
**Class: `IntelligenceFusionEngine`**
- `execute_fusion() -> pd.DataFrame`: Fuses ASTRA, SCADE, and Resilience. Calls `compute_confidence()` and `determine_threat_severity()`. Implements Hybrid Risk-Aware math. Outputs `scadex_final_intelligence.csv`.

## `src/explainability/xai_engine.py`
**Class: `XAIEngine`**
- `execute() -> pd.DataFrame`: Reverses the fusion logic. Invokes `root_cause_engine.py` and `action_engine.py`. Generates text payloads via `explanation_builder.py`. Outputs to `outputs/reports/` and `scadex_explanations.csv`.

## `src/benchmarking/scadex_benchmark.py`
**Class: `SCADEXBenchmark`**
- `execute()`: Invokes `comparison_engine`, `ablation_engine`, and `robustness_engine`. Computes ROC-AUC, PR-AUC, F1, and Resilience SLA correlations. Plots `matplotlib` curves to `outputs/figures/`.
