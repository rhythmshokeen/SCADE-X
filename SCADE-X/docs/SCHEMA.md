# SCADE-X Canonical Schema & Normalization

This document explains the unified schema design that harmonizes the outputs of ASTRA and SCADE into a single data structure, enabling unified cross-system intelligence and resilience reasoning.

## 1. The Normalization Challenge

ASTRA and SCADE have completely different output signatures:
- **ASTRA** outputs `fused_risk_scores.csv` (transformer scores, isolation forest risk, graph centrality) using continuous unbounded or normalized risk values (Higher = More Anomalous).
- **SCADE** outputs `results.csv` (control flow fitness, temporal Z-score penalties, amount drift) using bounded 0 to 1 conformance scores (Lower = More Anomalous).

Before fusion can occur, these disparate artifacts must be joined and structurally aligned.

## 2. Canonical Schema Definition

The schema mapping rules are enforced in `src/fusion/schema_registry.py`.

| Canonical Column | Source System | Source Artifact Column | Description | Normalization Strategy |
|-----------------|---------------|-----------------------|-------------|-----------------------|
| `case_id` | Both | `case_id` | Unique trace identifier. | Direct outer join. |
| `astra_risk_score` | ASTRA | `risk_score` | ASTRA's composite weighted sum risk. | Min-Max scaled to [0, 1]. |
| `behavioral_score` | ASTRA | `behavior_scaled` | Sequential anomaly score from Transformer. | Direct (already 0-1). |
| `iforest_score` | ASTRA | `iforest_scaled` | Statistical anomaly score. | Direct (already 0-1). |
| `graph_score` | ASTRA | `supplier_scaled` | Supplier topological risk. | Direct (already 0-1). |
| `astra_predicted_anomaly` | ASTRA | `predicted_anomaly` | ASTRA's binary anomaly flag. | Direct (Boolean). |
| `scade_composite_score`| SCADE | `composite_score` | SCADE's minimum-operator fusion score. | Direct (Lower is anomalous). |
| `cf_score` | SCADE | `cf_score` | Control flow token-replay fitness. | Direct (0-1). |
| `time_score` | SCADE | `time_score` | Temporal standard deviation conformance. | Direct (0-1). |
| `resource_score` | SCADE | `resource_score` | Segregation of duties & role score. | Direct (0-1). |
| `amount_score` | SCADE | `amount_score` | Amount drift conformance. | Direct (0-1). |
| `security_score` | SCADE | `security_score` | SIEM context penalty conformance. | Direct (0-1). |
| `scade_flagged` | SCADE | `flagged` | SCADE's binary anomaly flag. | Direct (Boolean). |
| `attack_type` | SCADE | `attack_type` | Categorical signature mapping. | Direct (String). |
| `is_ground_truth_anomaly`| SCADE | `is_anomaly` | Data generation label. | Direct (Boolean). |

## 3. Subsystem Translation Rules & Missing Values

The `schema_normalizer.py` implements the following rules:

1. **Alignment via Case ID**: `case_id` acts as the primary key. An outer join ensures that if a case only exists in one subsystem's output (e.g. SCADE filtered it due to missing values, or ASTRA crashed on a graph component), it is preserved.
2. **Missing Outputs Graceful Handling**: If an entire subsystem output is missing (e.g., ASTRA failed during orchestration), the normalizer still produces the dataframe with `NaN` filled for the missing columns. This ensures the downstream SCADE-X pipeline doesn't crash catastrophically.
3. **Score Scaling**: SCADE's scores are strictly bounded `[0, 1]`. ASTRA's `risk_score` is a weighted sum that can exceed 1.0. The normalizer detects this and applies Min-Max scaling to compress `astra_risk_score` into a strictly normalized `[0, 1]` range, ensuring fair mathematical evaluation.

## 4. Future Extensibility

The `SchemaRegistry` class uses Python dataclasses to easily extend fields. If a new intelligence module is added to SCADE-X (e.g., NLP extraction on invoice text), its output can simply be mapped in `SchemaRegistry.FIELDS` and it will automatically flow into `data/intermediate/unified_case_intelligence.csv`.
