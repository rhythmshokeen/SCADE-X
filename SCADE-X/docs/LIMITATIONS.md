# SCADE-X Limitations

While SCADE-X significantly advances supply chain intelligence, it suffers from several distinct architectural and theoretical limitations.

## 1. Causal Entanglement in Explainability
The XAI engine uses magnitude-based heuristics to determine root causes. However, it assumes that features are independent. In reality, a compromised credential (security score) *causes* the control flow deviation (skipped approval). SCADE-X currently tags both as concurrent causes without explicitly modeling the temporal causality between them.

## 2. Noise Sensitivity in Fusion
The Hybrid Risk-Aware fusion relies on a Max-Dominant algorithm. While smoothed, an extremely noisy false-positive from ASTRA (e.g. $0.99$ risk) will still exert heavy upward pressure on the final SCADE-X risk score. While resilience bounds this, adversarial noise can still degrade system precision.

## 3. Static Thresholding
The Decision Engine maps final risk to threat severity (`LOW`, `CRITICAL`) using statically defined thresholds (e.g. $> 0.85$). In production, operational baselines shift dynamically based on seasonality and volume. The thresholds should ideally be dynamically learned or calibrated, but are currently hardcoded heuristics.

## 4. Scalability Limits (Disk I/O)
Because SCADE-X employs an "Outside-In" orchestration architecture to preserve subsystem integrity, data is passed between ASTRA, SCADE, and SCADE-X via filesystem CSV dumps. In massive environments (e.g., 50 million cases/day), this heavy disk I/O will bottleneck performance. An enterprise refactor would require converting this to in-memory Kafka or Redis streams.

## 5. Dependency Assumptions
SCADE-X assumes that ASTRA and SCADE successfully align on the definition of a `case_id`. If ASTRA dynamically generates synthetic case IDs or filters them differently than SCADE, the `schema_normalizer.py` outer join will result in fragmented, incomplete intelligence rows, skewing the final benchmarking tables.
