# SCADE-X Research Contributions

## 1. System Novelty & Positioning

SCADE-X addresses a critical gap in Supply Chain Intelligence and Process Mining: **The inability of singular modeling paradigms to distinguish between process drift, intentional fraud, and systemic operational failure.**

### ASTRA vs. SCADE Limitations
- **ASTRA** relies on deep latent space embeddings (Transformers, Isolation Forests). While highly predictive of subtle behavioral anomalies, it fails to enforce rigid legal compliance (e.g. Segregation of Duties) because neural networks learn averages, not deterministic laws.
- **SCADE** relies on deterministic Petri Nets (Inductive Miner). While mathematically rigorous for detecting missing approvals or temporal violations, it is blind to context. A transaction that perfectly follows the rules but involves highly anomalous categorical values or central supplier behaviors will bypass SCADE entirely.

### The SCADE-X Contribution
SCADE-X proves that these two paradigms are not mutually exclusive, but synergistically foundational. By implementing **Hybrid Risk-Aware Fusion**, SCADE-X acts as the first framework to merge autoregressive behavioral detection with token-based process replay.

## 2. Core Contributions

1. **Resilience-Aware Anomaly Intelligence**: Traditional systems ask "Is this an anomaly?". SCADE-X asks "If this is an anomaly, will it shatter the supply chain?". SCADE-X introduces `Operational Fragility` and `Systemic Vulnerability` mathematically integrating SIEM security threats with Process Mining.
2. **Graph-Aware Disruption Reasoning**: SCADE-X translates ASTRA's topological supplier centrality scores into actionable disruption multipliers, demonstrating that an anomaly at a central node mathematically necessitates a higher threat SLA.
3. **Explainable Forensic Diagnostics (XAI)**: SCADE-X pioneers an evidence-based reverse-compiler. Rather than relying on black-box neural explainers (like SHAP) which confuse human auditors, SCADE-X deterministically maps localized failure magnitudes to human-readable markdown reports, accelerating triage resolution times.
4. **Decoupled Orchestration**: From an engineering standpoint, SCADE-X demonstrates a non-invasive orchestration schema. Subsystems maintain separate memory and execution boundaries, connected solely by schema-normalized data contracts.
