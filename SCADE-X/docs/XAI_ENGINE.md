# SCADE-X Explainability (XAI) Engine

This document details the architecture, forensic methodology, and design choices for the SCADE-X Explainability Layer, which translates high-dimensional mathematical risk scores into actionable, human-readable forensic intelligence.

---

## 1. System Purpose & Research Motivation

In high-stakes enterprise environments (procurement fraud, supply chain disruption), a "black-box" anomaly score of 0.95 is virtually useless to a human investigator. A forensic accountant or security analyst needs to know *why* a transaction was flagged, *what* broke, and *how* to fix it. 

The XAI engine converts the unified multi-layer intelligence (ASTRA, SCADE, Resilience, Fusion) into structured evidence trails, bridging the gap between machine learning and human decision-making.

---

## 2. Explanation Architecture

The XAI layer operates dynamically on the outputs of the Intelligence Fusion Engine. It consists of four distinct modules:

1. **Root Cause Engine** (`root_cause_engine.py`): Reverses the fusion equations to identify the specific feature vectors driving the risk scores.
2. **Action Engine** (`action_engine.py`): Maps the prescriptive `RecommendedAction` to a localized explanation of *why* that specific triage step was chosen.
3. **Explanation Builder** (`explanation_builder.py`): A modular text-generation factory that parses raw scores into domain-specific narrative sentences for ASTRA, SCADE, and Resilience.
4. **Case Report Generator** (`case_report_generator.py`): An automated documentation engine that builds persistent, immutable Markdown and JSON reports for case auditing.

---

## 3. Forensic Methodology & Root-Cause Reasoning

The engine avoids generic templates. It utilizes localized causal reasoning based directly on the mathematical thresholds defined in SCADE and ASTRA.

### Root Cause Logic
The `estimate_root_cause` function evaluates every risk dimension mathematically. It computes the "magnitude of deviation" for each perspective (e.g., $1.0 - \mathcal{S}_{\text{cf}}$ for process compliance, or $\mathcal{A}_{\text{behavioral}}$ for transformer deviation). The dimension with the highest magnitude is tagged as the **Primary Cause**. All other dimensions exceeding the $0.875$ failure threshold (or $0.8$ risk threshold) are tagged as **Secondary Causes**.

### Recommendation Reasoning
The `action_engine.py` explicitly grounds its text in the mathematical drivers of the decision engine. If `CREDENTIAL_RESET` is recommended, the engine mathematically verifies the SIEM security penalty and embeds that specific score in the text to prove the recommendation is evidence-based, not hallucinated.

---

## 4. Multi-Layer Explainability

The structured reports decompose the anomaly into four distinct cognitive layers:

### A. Behavioral Intelligence (ASTRA)
Explains the continuous latent variables. 
*Example:* "Transformer sequence analysis detected highly abnormal latent behavior. Isolation Forest flagged extreme statistical feature deviations."

### B. Process Conformance (SCADE)
Explains the deterministic structural variables.
*Example:* "Control Flow Replay failed (Fitness: 0.65), indicating skipped or extra steps. Segregation of Duties violated."

### C. Supply Chain Resilience
Explains the systemic business implications.
*Example:* "Systemic Vulnerability is 0.82. Disruption propagation likelihood is high. Supplier dependency exposure is critical."

### D. Confidence & Final Decision
Explains the fusion layer's mathematical consensus.
*Example:* "High Confidence: Strong alignment between ASTRA behavioral modeling and SCADE deterministic rules."

---

## 5. Output Datasets

The engine produces two output types:
1. `data/processed/scadex_explanations.csv`: A flattened, tabular dataset containing the root causes, explanations, and summaries for all processed cases. Useful for analytics dashboards.
2. `outputs/reports/{case_id}.json / .md`: Individual, deeply structured forensic reports generated for any case requiring escalation (`STANDARD`, `URGENT`, or `IMMEDIATE`). These are the primary artifacts for human investigators.

---

## 6. Limitations

1. **Deterministic Text Generation**: The current explanation builder uses rule-based text interpolation rather than an LLM. While this guarantees zero hallucination (a strict requirement for forensic auditing), the language may feel repetitive across highly similar cases.
2. **Causal Entanglement**: The root cause engine assumes features are independent when ranking magnitudes. In reality, a compromised credential (security score) *causes* the control flow deviation (skipped approval). The current engine identifies them both as causes, but does not explicitly model the temporal causality between them.
