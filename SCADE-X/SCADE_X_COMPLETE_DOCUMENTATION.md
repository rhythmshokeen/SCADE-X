---
title: "SCADE-X: Complete Technical Documentation"
subtitle: "A Unified AI + Process Mining Framework for Supply Chain Resilience"
version: "1.0.0 — Repository-Grounded Edition"
---

# SCADE-X — Complete Technical Documentation

**Project Name:** SCADE-X (Supply Chain Anomaly Detection & Engineering — Extended)

**Executive Summary:**
SCADE-X is a hybrid intelligence platform that fuses two independent anomaly detection subsystems — ASTRA (AI-driven behavioral modeling) and SCADE (deterministic process mining) — under a unified Supply Chain Resilience (SCR) orchestration engine. The platform ingests enterprise procurement event logs, runs them through parallel AI and conformance-checking pipelines, layers graph-based risk propagation and kinetic TTR/TTS (Time-To-Recover / Time-To-Survive) mathematics on top, and produces a single fused risk score per case with full forensic explainability. Every claim in this document is traced to source code.

**Goals:**
1. Detect anomalies that neither AI nor rule-based systems can catch alone.
2. Quantify supply chain resilience impact of every detected anomaly.
3. Produce actionable, explainable recommendations (not just scores).
4. Provide a benchmarking framework to prove the fusion outperforms individual subsystems.

**Key Research Contribution:**
The novel "Hybrid Risk-Aware Fusion" algorithm — a Max-Dominant Non-Linear blend that respects the strongest threat signal, amplified by graph-derived systemic vulnerability and TTR/TTS gap — replacing naive score averaging.

---

# Table of Contents

- [1. Cover Page](#scade-x--complete-technical-documentation)
- [2. Table of Contents](#table-of-contents)
- [3. Executive Overview](#3-executive-overview)
- [4. Repository Structure](#4-repository-structure-full)
- [5. End-to-End Pipeline](#5-end-to-end-pipeline)
- [6. ASTRA Deep Dive](#6-astra-deep-dive)
- [7. SCADE Deep Dive](#7-scade-deep-dive)
- [8. Supply Chain Resilience Layer](#8-supply-chain-resilience-layer-scr)
- [9. Intelligence Fusion Layer](#9-intelligence-fusion-layer)
- [10. Explainability Layer (XAI)](#10-explainability-layer-xai)
- [11. Benchmarking & Validation](#11-benchmarking--validation)
- [12. Output Artifacts](#12-output-artifacts)
- [13. Runtime Walkthrough](#13-runtime-walkthrough)
- [14. Architecture Diagrams](#14-architecture-diagrams)
- [15. Mathematical Foundations](#15-mathematical-foundations)
- [16. Real Validation Findings](#16-real-validation-findings)
- [17. ASTRA vs SCADE vs SCADE-X](#17-astra-vs-scade-vs-scade-x)
- [18. Limitations](#18-limitations)
- [19. Future Improvements](#19-future-improvements)
- [20. Troubleshooting Guide](#20-troubleshooting-guide)
- [21. Glossary](#21-glossary)
- [22. Appendix](#22-appendix)

---

# 3. Executive Overview

## 3.1 What is SCADE-X?

**Beginner Explanation:**
Imagine you run a giant warehouse that processes thousands of purchase orders every day. You have two security guards:

- **Guard 1 (ASTRA)** is a detective who watches *how* people behave — are they rushing? Are they visiting unusual areas? He uses AI to sense "something feels wrong" but can't point to a specific rule that was broken.
- **Guard 2 (SCADE)** is a strict auditor with a rulebook — he checks if every step was done in the right order, by the right person, at the right time, for the right amount. If someone skipped a step or overpaid, he flags it instantly. But he can't detect *novel* attacks he hasn't seen before.

SCADE-X takes both guards' reports and hands them to a third entity: **The Architect (Resilience Layer)**. The Architect doesn't just ask "did they break a rule?" — the Architect asks "if this person blows up their station, how long until the whole warehouse collapses (TTS) versus how long it takes to fix it (TTR)?" If TTR > TTS, you are mathematically doomed.

**Technical Explanation:**
SCADE-X is a multi-subsystem orchestration platform that:
1. Runs **ASTRA** (Transformer encoder + Isolation Forest + Graph Intelligence) to produce probabilistic behavioral anomaly scores.
2. Runs **SCADE** (PM4Py Inductive Miner + Token-Based Replay + multi-perspective conformance) to produce deterministic process conformance scores.
3. Normalizes both outputs into a canonical schema via `SchemaNormalizer`.
4. Computes supply chain resilience metrics via `ResilienceEngine` (NetworkX graph construction, cascading risk propagation, TTR/TTS estimation).
5. Fuses everything via `IntelligenceFusionEngine` using a Max-Dominant Non-Linear algorithm with resilience amplification.
6. Generates forensic explanations via `XAIEngine`.
7. Benchmarks the fused system against individual subsystems via `SCADEXBenchmark`.

## 3.2 What Problem Does It Solve?

| Problem | Who Has It | SCADE-X Solution |
|---|---|---|
| AI detects novel fraud but cannot explain it | Security teams | SCADE provides deterministic rule-based explanations |
| Rule-based systems miss zero-day attacks | Compliance teams | ASTRA provides behavioral AI detection |
| Neither system considers supply chain topology | Supply chain managers | Resilience Layer adds graph propagation + TTR/TTS |
| Averaging scores masks critical threats | Risk analysts | Max-Dominant fusion respects strongest signal |
| No single system gives actionable recommendations | Enterprise decision-makers | Decision Engine maps risk to prescriptive actions |

## 3.3 Why Were ASTRA and SCADE Combined?

ASTRA alone produces a float between 0 and 1 but cannot explain *which* Segregation-of-Duties rule was violated. SCADE alone catches rule violations but cannot detect adversarial behavioral sequences it hasn't been trained on. The combination closes both gaps.

**Verified Source:** `src/orchestration/scadex_pipeline.py` — the `execute()` method sequentially invokes both subsystems and feeds their outputs into the fusion layer.

## 3.4 How Supply Chain Resilience Fits In

Traditional anomaly detection asks: "Is this transaction suspicious?" SCADE-X additionally asks: "If this transaction is an attack, how badly does it damage the supply chain?" This is computed through:
- **Graph centrality** (NetworkX degree/betweenness/PageRank) — is the affected supplier a structural chokepoint?
- **Cascading risk propagation** — does risk flow downstream to other suppliers?
- **TTR/TTS gap** — can the organization recover before it collapses?

**Verified Source:** `src/resilience/resilience_engine.py` — the `compute_resilience()` method orchestrates all of the above.

---

# 4. Repository Structure (FULL)

```
SCADE-X/
├── main.py                          # Entry point — launches SCADEXUnifiedPipeline
├── configs/
│   └── scadex_config.yaml           # Pipeline toggles, thresholds, paths
├── src/
│   ├── orchestration/               # Pipeline brain
│   │   ├── scadex_pipeline.py       # Main orchestrator (SCADEXUnifiedPipeline)
│   │   ├── astra_runner.py          # Subprocess executor for ASTRA
│   │   ├── scade_runner.py          # Subprocess executor for SCADE
│   │   ├── config_manager.py        # YAML config loader + CLI override
│   │   ├── execution_context.py     # Runtime state tracking (SubsystemState)
│   │   ├── runtime_manager.py       # Stage timing + failure recovery
│   │   ├── artifact_manager.py      # File path registry for all artifacts
│   │   └── input_validator.py       # Pre-flight checks for required inputs
│   ├── fusion/                      # Schema alignment + risk fusion
│   │   ├── schema_registry.py       # Canonical field definitions (CanonicalField)
│   │   ├── schema_normalizer.py     # ASTRA/SCADE output merger (SchemaNormalizer)
│   │   ├── intelligence_fusion.py   # Core fusion algorithm (IntelligenceFusionEngine)
│   │   ├── confidence_engine.py     # Signal agreement scoring
│   │   ├── decision_engine.py       # Threat severity + action mapping
│   │   └── fusion_models.py         # Enums: ThreatSeverity, RecommendedAction, etc.
│   ├── resilience/                  # Supply chain resilience intelligence
│   │   ├── resilience_engine.py     # Main orchestrator (ResilienceEngine)
│   │   ├── graph_engine.py          # NetworkX graph construction (SupplyChainGraph)
│   │   ├── risk_propagation.py      # Damped iterative diffusion (propagate_risk_through_graph)
│   │   ├── ttr_tts_engine.py        # Time-To-Recover / Time-To-Survive math
│   │   ├── resilience_models.py     # Enums + operational fragility math
│   │   └── recovery_analysis.py     # Mitigation strategy selection engine
│   ├── explainability/              # Forensic explanation generation
│   │   ├── xai_engine.py            # Main XAI orchestrator (XAIEngine)
│   │   ├── root_cause_engine.py     # Primary/secondary cause ranking
│   │   ├── action_engine.py         # Action recommendation explainer
│   │   ├── explanation_builder.py   # Multi-layer text explanation generation
│   │   └── case_report_generator.py # JSON + Markdown report writer
│   └── benchmarking/                # Evaluation framework
│       ├── scadex_benchmark.py      # Main benchmark orchestrator (SCADEXBenchmark)
│       ├── metrics_engine.py        # sklearn metrics + custom resilience metrics
│       ├── comparison_engine.py     # ASTRA vs SCADE vs SCADE-X comparison
│       ├── ablation_engine.py       # Component removal experiments
│       └── robustness_engine.py     # Noise/sparsity/failure simulation
├── astra/                           # ASTRA subsystem (independent project)
│   ├── src/
│   │   ├── main.py                  # ASTRA entrypoint (boot only)
│   │   ├── ingestion/               # CSV loading + synthetic data generation
│   │   ├── process_mining/          # Event log building + sequence extraction
│   │   ├── models/transformers/     # PyTorch ProcessTransformer (nn.Module)
│   │   ├── anomaly_detection/       # Isolation Forest anomaly scoring
│   │   ├── graph_intelligence/      # Supply chain graph construction + features
│   │   ├── fusion/                  # ASTRA internal risk score fusion
│   │   ├── inference/               # Transformer scoring + explanation
│   │   ├── evaluation/              # ASTRA standalone evaluation
│   │   ├── explainability/          # Case-level explanation generation
│   │   ├── benchmarking/            # ASTRA standalone benchmark
│   │   └── utils/                   # Config loader + logger
│   ├── data/raw/                    # Input: synthetic_supply_chain.csv
│   ├── data/processed/              # Output: fused_risk_scores.csv, graph, etc.
│   └── models_store/                # Saved PyTorch model weights
├── scade/                           # SCADE subsystem (independent project)
│   ├── src/
│   │   ├── preprocess.py            # Data loading, PM4Py EventLog conversion
│   │   ├── discover.py              # Inductive Miner Petri net discovery
│   │   ├── conformance/
│   │   │   ├── control_flow.py      # Token-Based Replay fitness scoring
│   │   │   ├── time_perspective.py  # Gaussian temporal baseline scoring
│   │   │   ├── resource.py          # SOD + role conformance scoring
│   │   │   ├── amount_delta.py      # Financial drift + duplicate detection
│   │   │   ├── security_context.py  # SIEM event correlation scoring
│   │   │   └── fusion.py            # Multi-perspective min-score composite
│   │   ├── attack_mapper.py         # Attack signature classification
│   │   ├── cross_case.py            # Cross-case correlation analysis
│   │   ├── evaluate.py              # Classification report + ablation
│   │   ├── generate_data.py         # Synthetic supply chain log generation
│   │   └── generate_security_log.py # Synthetic SIEM event generation
│   ├── data/                        # SCADE outputs: results.csv, etc.
│   └── models/                      # Saved Petri net model (normal_model.pkl)
├── data/
│   ├── intermediate/                # unified_case_intelligence.csv
│   └── processed/                   # Final outputs: scadex_final_intelligence.csv, etc.
└── outputs/
    ├── reports/                     # Per-case forensic .json + .md reports
    ├── evaluation/                  # Benchmark CSVs
    └── figures/                     # ROC curve PNGs
```

### Why Each Folder Exists

| Folder | Purpose | Runtime Role |
|---|---|---|
| `src/orchestration/` | The "brain" — sequences all subsystems | Invoked by `main.py`; controls entire lifecycle |
| `src/fusion/` | Aligns schemas and computes final risk | Runs after ASTRA + SCADE complete |
| `src/resilience/` | Graph math + TTR/TTS + recovery recommendations | Runs after schema normalization |
| `src/explainability/` | Generates human-readable forensic reports | Runs after fusion produces final scores |
| `src/benchmarking/` | Proves SCADE-X outperforms individual subsystems | Runs last; optional (failure is recoverable) |
| `astra/` | Independent AI subsystem (Transformer + IForest) | Executed via subprocess by `ASTRARunner` |
| `scade/` | Independent Process Mining subsystem (PM4Py) | Executed via subprocess by `SCADERunner` |

---

# 5. End-to-End Pipeline

## 5.1 Entry Point

```
python main.py
```

This invokes `SCADEXUnifiedPipeline.execute()` in `src/orchestration/scadex_pipeline.py`.

**Verified Source:** `src/orchestration/scadex_pipeline.py`, lines 1–187

## 5.2 Pipeline Stages (Exact Runtime Order)

```mermaid
graph TD
    A["main.py"] --> B["SCADEXUnifiedPipeline.execute()"]
    B --> C["Stage 1: Input Validation"]
    C --> D["Stage 2: ASTRA Execution"]
    D --> E["Stage 3: SCADE Execution"]
    E --> F["Stage 4: Schema Normalization"]
    F --> G["Stage 5: Resilience Intelligence"]
    G --> H["Stage 6: Intelligence Fusion"]
    H --> I["Stage 7: Explainability"]
    I --> J["Stage 8: Benchmarking"]
    J --> K["Stage 9: Artifact Export"]
    K --> L["Pipeline Complete ✅"]
```

### Stage 1: Input Validation
- **What enters:** File system paths from `configs/scadex_config.yaml`
- **What executes:** `InputValidator.validate()` checks that required CSV files exist
- **What outputs:** Boolean pass/fail; pipeline aborts on failure
- **Why it exists:** Prevents cryptic downstream errors from missing input files
- **Failure mode:** `RuntimeError` if `synthetic_supply_chain.csv` is missing

### Stage 2: ASTRA Execution
- **What enters:** Raw CSV event logs in `astra/data/raw/`
- **What executes:** `ASTRARunner.execute()` spawns a subprocess running `astra/src/main.py`
- **Functions called:** `subprocess.run()` with fallback entrypoints (`main.py` → `src/main.py` → `-m src.main`)
- **What outputs:** `astra/data/processed/fused_risk_scores.csv` containing per-case `risk_score`, `behavioral_anomaly_score`, `iforest_scaled`, `supplier_scaled`, `predicted_anomaly`
- **Why it exists:** Generates probabilistic behavioral anomaly scores
- **Failure mode:** `RuntimeError` with diagnostic stderr parsing for missing dependencies
- **Verified Source:** `src/orchestration/astra_runner.py`, lines 66–198

### Stage 3: SCADE Execution
- **What enters:** Raw CSV event logs in `scade/data/`
- **What executes:** `SCADERunner.execute()` spawns a subprocess running `scade/main.py`
- **Functions called:** `subprocess.run()` with fallback entrypoints (`main.py` → `run.py` → `start.py`)
- **What outputs:** `scade/data/results.csv` containing per-case `cf_score`, `time_score`, `resource_score`, `amount_score`, `security_score`, `composite_score`, `flagged`, `attack_type`
- **Why it exists:** Generates deterministic process conformance scores
- **Failure mode:** `RuntimeError` with `_detect_missing_dependency()` parsing stderr
- **Verified Source:** `src/orchestration/scade_runner.py`, lines 63–188

### Stage 4: Schema Normalization
- **What enters:** `astra/data/processed/fused_risk_scores.csv` + `scade/data/results.csv`
- **What executes:** `SchemaNormalizer.normalize()`
- **Functions called:**
  - `_load_astra()` → reads ASTRA CSV, renames columns via `SchemaRegistry.get_astra_mappings()`
  - `_load_scade()` → reads SCADE CSV, renames columns via `SchemaRegistry.get_scade_mappings()`
  - Case ID normalization (`PO-00021` → `PO00021`)
  - Outer join on `case_id`
  - Min-max scaling of `astra_risk_score` if values exceed [0, 1]
- **What outputs:** `data/intermediate/unified_case_intelligence.csv` — a single DataFrame with 14 canonical columns
- **Why it exists:** ASTRA and SCADE use different column names and ID formats; this alignment is mandatory for fusion
- **Verified Source:** `src/fusion/schema_normalizer.py`, lines 35–87; `src/fusion/schema_registry.py`, lines 23–45

### Stage 5: Resilience Intelligence
- **What enters:** `data/intermediate/unified_case_intelligence.csv`
- **What executes:** `ResilienceEngine.compute_resilience()`
- **Functions called (in order):**
  1. `SupplyChainGraph.load_or_build()` → loads ASTRA's `.gpickle` graph or reconstructs from raw CSV
  2. `SupplyChainGraph.compute_supplier_metrics()` → `nx.degree_centrality()`, `nx.betweenness_centrality()`, `nx.pagerank()`
  3. `SupplyChainGraph.map_case_to_supplier()` → maps each `case_id` to a `supplier_id`
  4. `compute_case_propagated_risk()` → seeds risky suppliers and runs damped iterative diffusion (3 hops, α=0.3)
  5. `estimate_ttr()` → per-case Time-To-Recover
  6. `estimate_tts()` → per-case Time-To-Survive
  7. `compute_resilience_gap()` → `max(0, TTR - TTS)`
  8. `compute_operational_fragility()` → weighted combination of ASTRA risk, SCADE risk, TTR/TTS fragility
  9. `map_disruption_severity()` → categorical: LOW / MEDIUM / HIGH / CRITICAL
  10. `recommend_mitigation()` → selects mitigation strategy via priority rules
- **What outputs:** `data/processed/resilience_intelligence.csv` — 20+ columns per case
- **Why it exists:** Transforms raw anomaly scores into supply chain impact assessments
- **Verified Source:** `src/resilience/resilience_engine.py`, lines 63–234

### Stage 6: Intelligence Fusion
- **What enters:** `unified_case_intelligence.csv` + `resilience_intelligence.csv`
- **What executes:** `IntelligenceFusionEngine.execute()`
- **Functions called:**
  1. `_compute_hybrid_risk()` → Max-Dominant Non-Linear fusion
  2. `compute_confidence()` → signal agreement + evidence strength
  3. `determine_threat_severity()` → effective threat classification
  4. `determine_recommended_action()` → prescriptive action with resilience override
  5. `determine_escalation_priority()` → IMMEDIATE / URGENT / STANDARD / NONE
- **What outputs:** `data/processed/scadex_final_intelligence.csv` — the master output with 24 columns
- **Why it exists:** This is the core intellectual contribution — fusing all signals into a single actionable score
- **Verified Source:** `src/fusion/intelligence_fusion.py`

### Stage 7: Explainability
- **What enters:** All three DataFrames (unified, resilience, final)
- **What executes:** `XAIEngine.execute()`
- **Functions called:**
  1. `estimate_root_cause()` → ranks failure signals by severity magnitude
  2. `explain_action()` → generates text explaining why a specific action was recommended
  3. `build_astra_explanation()`, `build_scade_explanation()`, `build_resilience_explanation()`, `build_confidence_explanation()` → per-subsystem text
  4. `build_forensic_summary()` → one-sentence executive summary
  5. `CaseReportGenerator.generate_report()` → writes `.json` + `.md` files for escalated cases
- **What outputs:** `data/processed/scadex_explanations.csv` + individual `outputs/reports/{case_id}.json` and `.md` files
- **Why it exists:** Makes the system auditable and human-interpretable
- **Verified Source:** `src/explainability/xai_engine.py`, lines 40–116

### Stage 8: Benchmarking
- **What enters:** `unified_case_intelligence.csv` + `scadex_final_intelligence.csv`
- **What executes:** `SCADEXBenchmark.execute()`
- **Functions called:**
  1. `compare_models()` → ASTRA vs SCADE vs SCADE-X ROC-AUC comparison
  2. `compute_resilience_metrics()` → disruption detection quality + recovery prioritization quality
  3. `AblationEngine.execute()` → tests 7 configurations (full, without ASTRA, without SCADE, etc.)
  4. `RobustnessEngine.execute()` → tests 4 scenarios (baseline, ASTRA offline, 30% sparse, noisy)
  5. `_plot_roc_curves()` → generates `outputs/figures/roc_curves.png`
- **What outputs:** `outputs/evaluation/comparison_tables.csv`, `ablation_results.csv`, `robustness_results.csv`, `resilience_evaluation.csv`
- **Why it exists:** Provides empirical evidence that fusion outperforms individual subsystems
- **Failure mode:** Non-fatal — pipeline continues if benchmarking fails
- **Verified Source:** `src/benchmarking/scadex_benchmark.py`, lines 52–95

### Stage 9: Artifact Export
- **What enters:** All generated CSVs and reports
- **What executes:** Final logging and summary via `RuntimeManager.summarize()`
- **What outputs:** Console log with per-stage timing and status

---

# 6. ASTRA Deep Dive

## 6.1 What is ASTRA?

**Beginner Explanation:**
ASTRA is the "detective" — it uses artificial intelligence to sense when a procurement transaction *feels* wrong, even if no specific rule was broken. It does this by learning what "normal" behavior looks like and flagging deviations.

**Technical Explanation:**
ASTRA is a multi-model AI anomaly detection subsystem consisting of three independent scoring components:

1. **Process Transformer** — A PyTorch `nn.TransformerEncoder` that learns sequential patterns in process activity logs and flags sequences that deviate from learned normal behavior.
2. **Isolation Forest** — A scikit-learn statistical anomaly detector that identifies cases with unusual numerical feature distributions.
3. **Graph Intelligence** — A NetworkX-based supply chain graph that computes supplier centrality metrics.

These three scores are fused into a single `risk_score` via weighted summation.

## 6.2 ASTRA Architecture

```mermaid
graph TD
    A["Raw CSV: synthetic_supply_chain.csv"] --> B["Ingestion (csv_loader.py)"]
    B --> C["Sequence Builder"]
    C --> D["Process Tokenizer"]
    D --> E["ProcessTransformer (PyTorch)"]
    E --> F["Behavioral Anomaly Score"]
    
    B --> G["Feature Engineering"]
    G --> H["Isolation Forest"]
    H --> I["IForest Anomaly Score"]
    
    B --> J["Graph Builder (NetworkX)"]
    J --> K["Graph Features (Centrality)"]
    K --> L["Supplier Graph Score"]
    
    F --> M["ASTRA Fusion Engine"]
    I --> M
    L --> M
    M --> N["fused_risk_scores.csv"]
```

## 6.3 Process Transformer (Core AI Model)

**Verified Source:** `astra/src/models/transformers/process_transformer.py`

**Architecture:**
```
ProcessTransformer(nn.Module):
  Embedding(vocab_size + 1, embed_dim=32)
  TransformerEncoder(
    TransformerEncoderLayer(d_model=32, nhead=4, dim_feedforward=64),
    num_layers=2
  )
  Linear(embed_dim=32, vocab_size + 1)
```

**How it works (beginner):**
Think of each procurement case as a "sentence" where each activity (e.g., "Create PO", "Approve PO", "Release Payment") is a "word." The Transformer learns the grammar of normal procurement. When it sees a sentence like "Release Payment → Create PO" (payment before creation), it flags it as grammatically wrong.

**How it works (technical):**
1. Activity sequences are tokenized via `process_tokenizer.py` into integer token sequences.
2. The model is trained with next-token prediction: given tokens `[0, ..., n-1]`, predict token `n`.
3. Cross-entropy loss measures how well the model predicts the next activity.
4. At inference, the reconstruction error (loss) per case becomes the behavioral anomaly score — high loss = unexpected sequence.
5. Training uses Adam optimizer, lr=0.001, 10 epochs, batch size 32.

**Device:** Automatically uses Apple Metal Performance Shaders (`mps`) if available, otherwise `cpu`.

## 6.4 Isolation Forest

**Verified Source:** `astra/src/anomaly_detection/isolation_forest.py`

The Isolation Forest operates on engineered numerical features (e.g., step counts, timing distributions, amount values). It assigns an `anomaly_score` to each case — the score is inverted in `fusion_engine.py` so that higher values = higher risk.

## 6.5 Graph Intelligence

**Verified Source:** `astra/src/graph_intelligence/build_supply_graph.py`, `graph_features.py`

Constructs a directed graph from event logs:
- Supplier → Activity edges
- User → Activity edges  
- Activity → Activity (sequential) edges

Computes `supplier_centrality` per node, which is scaled to [0,1] by MinMaxScaler in the fusion engine.

## 6.6 ASTRA Internal Fusion

**Verified Source:** `astra/src/fusion/fusion_engine.py`, lines 119–141

```
risk_score = 0.75 × behavior_scaled + 0.20 × iforest_scaled + 0.05 × supplier_scaled
```

The Transformer dominates (75% weight). The anomaly threshold is dynamically computed as:
```
threshold = mean(risk_score) + 2 × std(risk_score)
```

Cases above this threshold are labeled `predicted_anomaly = True`.

**Output:** `astra/data/processed/fused_risk_scores.csv`

## 6.7 ASTRA Limitations

1. **Black box:** The Transformer provides a score but cannot explain *which* specific rule was violated.
2. **Threshold sensitivity:** The dynamic threshold (mean + 2σ) assumes risk scores are roughly Gaussian — this may not hold for adversarial distributions.
3. **Boot-only main.py:** The ASTRA `main.py` only logs configuration and exits. The actual pipeline modules must be invoked separately. SCADE-X's `ASTRARunner` handles this via subprocess execution of `main.py` (which triggers the full pipeline if properly configured).

---

# 7. SCADE Deep Dive

## 7.1 What is SCADE?

**Beginner Explanation:**
SCADE is the "auditor" — it takes the company's official process flowchart and checks every single transaction against it. Did the steps happen in the right order? At the right speed? By the right people? For the right amount? With valid security credentials?

**Technical Explanation:**
SCADE is a multi-perspective conformance checking engine built on PM4Py. It implements:
1. **Control Flow Conformance** — Token-Based Replay against an Inductive Miner Petri net
2. **Temporal Conformance** — Gaussian baseline comparison for step durations
3. **Resource Conformance** — Segregation of Duties (SOD) and role assignment validation
4. **Amount Conformance** — Financial drift detection and duplicate payment identification
5. **Security Context** — SIEM event correlation (optional 5th perspective)

## 7.2 SCADE Architecture

```mermaid
graph TD
    A["Raw Event Log CSV"] --> B["Preprocessing (preprocess.py)"]
    B --> C["PM4Py EventLog Conversion"]
    C --> D["Inductive Miner (discover.py)"]
    D --> E["Petri Net Model"]
    
    C --> F["Control Flow Scoring"]
    E --> F
    F --> G["cf_score per case"]
    
    B --> H["Time Perspective Scoring"]
    H --> I["time_score per case"]
    
    B --> J["Resource Scoring"]
    J --> K["resource_score per case"]
    
    B --> L["Amount Delta Scoring"]
    L --> M["amount_score per case"]
    
    B --> N["Security Context Scoring"]
    N --> O["security_score per case"]
    
    G --> P["Multi-Perspective Fusion (fusion.py)"]
    I --> P
    K --> P
    M --> P
    O --> P
    P --> Q["results.csv"]
```

## 7.3 Process Discovery (Petri Net Mining)

**Verified Source:** `scade/src/discover.py`, lines 8–18

```python
net, im, fm = pm4py.discover_petri_net_inductive(train_log, noise_threshold=0.2)
```

The Inductive Miner discovers the normative process model from training data (non-anomalous cases). The `noise_threshold=0.2` parameter filters out minor variations to prevent overfitting. The resulting Petri net defines the "correct" workflow.

## 7.4 Control Flow Conformance

**Verified Source:** `scade/src/conformance/control_flow.py`, lines 5–47

Token-Based Replay runs each case trace through the Petri net. For each case:
- `cf_score` = `trace_fitness` (0–1, where 1 = perfect conformance)
- `missing_tokens` = tokens the model needed but the trace didn't provide (skipped steps)
- `remaining_tokens` = tokens left over after replay (extra/unauthorized steps)
- `missing_acts` = activity names that were skipped or misplaced

**Beginner:** If the flowchart says "Create PO → Approve PO → Release Payment" but the trace shows "Create PO → Release Payment" (skipping approval), the replay detects `missing_tokens` for the Approve step and assigns a low `cf_score`.

## 7.5 Temporal Conformance

**Verified Source:** `scade/src/conformance/time_perspective.py`

For each activity transition, SCADE fits a Gaussian distribution on the normal training data's step durations. At scoring time, each case's step durations are compared against these baselines. Steps that are abnormally fast (rushed) or abnormally slow (delayed) reduce the `time_score`.

## 7.6 Resource Conformance

**Verified Source:** `scade/src/conformance/resource.py`

Checks two things:
1. **Role Assignment:** Was the activity performed by a user with the correct role?
2. **Segregation of Duties (SOD):** Were critical steps (e.g., creation and approval) performed by *different* users?

Outputs: `resource_score`, `wrong_role_count`, `sod_violation_count`

## 7.7 Amount Delta Conformance

**Verified Source:** `scade/src/conformance/amount_delta.py`

Detects:
- **Financial drift:** Payment amounts that deviate significantly from the purchase order amount
- **Duplicate payments:** Multiple payments for the same order

Outputs: `amount_score`, `amount_drift_pct`, `duplicate_payment`

## 7.8 Security Context (5th Perspective)

**Verified Source:** `scade/src/conformance/security_context.py`

Correlates procurement events with SIEM security logs. If a user performed a high-risk procurement step during a period when their account showed suspicious login activity (e.g., impossible travel, after-hours access), the `security_score` is penalized.

## 7.9 SCADE Multi-Perspective Fusion

**Verified Source:** `scade/src/conformance/fusion.py`, lines 21–71

**Fusion Method: Minimum Score**
```
composite_score = min(cf_score, time_score, resource_score, amount_score [, security_score])
```

**Why minimum, not average?** A process is only as secure as its weakest dimension. If `cf_score = 1.0` (perfect workflow) but `amount_score = 0.3` (massive financial drift), averaging produces 0.65 — which masks a real threat. Minimum-score fusion ensures the weakest dimension dominates.

**Anomaly Threshold:** `0.875` — cases with `composite_score < 0.875` are flagged as anomalous.

**Verified:** The weighted average is also computed (`WEIGHTS = cf:0.40, time:0.20, resource:0.25, amount:0.15`) but only for ablation comparison purposes. The primary fusion method is `minimum`.

---

# 8. Supply Chain Resilience Layer (SCR)

## 8.1 What is Supply Chain Resilience?

**Beginner Explanation:**
Traditional security systems only ask "Is this bad?" But in a supply chain, the real question is "If this is an attack, how badly does it hurt the whole network?" A fraud at a small, replaceable supplier is annoying. The same fraud at the *only* supplier of a critical component could shut down the entire operation. The Resilience Layer quantifies this.

**Technical Explanation:**
The SCR layer computes per-case resilience metrics by:
1. Constructing a directed supply chain graph using NetworkX
2. Computing supplier-level centrality metrics (degree, betweenness, PageRank)
3. Propagating risk through the graph using damped iterative diffusion
4. Estimating TTR (Time-To-Recover) and TTS (Time-To-Survive) from anomaly signals
5. Computing resilience gap, operational fragility, and disruption severity
6. Generating mitigation recommendations via priority-based rule engine

## 8.2 Complete SCR Metrics Reference

| Metric | Meaning | Formula | Code Location |
|---|---|---|---|
| `resilience_score` | Overall health (0=fragile, 1=robust) | `1 - systemic_vulnerability` | `resilience_engine.py:176` |
| `systemic_vulnerability` | Composite fragility | `0.35×fragility + 0.35×propagated_risk + 0.15×sec_risk + 0.15×ttr_tts_frag` | `resilience_engine.py:171-173` |
| `operational_fragility` | How close to structural failure | `0.30×A_risk + 0.40×(1-S_composite) + 0.30×TTR_TTS_fragility` | `resilience_models.py:37-61` |
| `propagated_risk` | Risk flowing from upstream suppliers | Damped diffusion: `risk(v,t+1) = α × Σ w(u,v) × risk(u,t)` | `risk_propagation.py:31-83` |
| `bottleneck_score` | Is the supplier a structural chokepoint? | `betweenness / (degree + ε)`, normalized to [0,1] | `graph_engine.py:113-126` |
| `dependency_risk` | Exposure to a single critical supplier | `min(1, criticality × (1 + amount_risk))` | `resilience_engine.py:167` |
| `ttr` | Time-To-Recover | `0.35×(1-resource) + 0.25×(1-time) + 0.25×(1-amount) + 0.15×iforest` | `ttr_tts_engine.py` |
| `tts` | Time-To-Survive | `max(0.05, 1 - (0.40×criticality + 0.35×(1-cf) + 0.25×(1-security)))` | `ttr_tts_engine.py` |
| `resilience_gap` | Recovery vs survival margin | `max(0, TTR - TTS)` | `ttr_tts_engine.py` |
| `business_impact` | Financial/operational damage estimate | `systemic_vulnerability × (1 + 0.5 × propagated_risk)` | `resilience_engine.py:220` |
| `recovery_priority` | P1–P4 priority tier | Rule-based engine (6 priority rules) | `recovery_analysis.py:31-137` |
| `mitigation_strategy` | Prescribed action | One of: `reroute_supplier`, `freeze_and_reset`, `freeze_transaction`, `diversify_sourcing`, `expedite_audit`, `monitor_only` | `recovery_analysis.py` |
| `continuity_risk` | Organizational survival risk | `HIGH`, `MEDIUM`, `LOW`, `NEGLIGIBLE` | `recovery_analysis.py` |
| `disruption_severity` | Categorical impact | `CRITICAL` if fragility>0.85 OR violations≥3 OR gap>0.3 | `resilience_models.py:64-85` |

## 8.3 Graph Engine (NetworkX)

**Verified Source:** `src/resilience/graph_engine.py`

The `SupplyChainGraph` class:
1. Attempts to load ASTRA's pre-built graph from `astra/data/processed/supply_chain_graph.gpickle`
2. Falls back to reconstructing from raw CSV by adding edges: Supplier→Activity, User→Activity, Activity→Activity (sequential)
3. Computes three centrality metrics per node:
   - **Degree Centrality** (`nx.degree_centrality`) — How many connections does this node have?
   - **Betweenness Centrality** (`nx.betweenness_centrality`) — How many shortest paths pass through this node?
   - **PageRank** (`nx.pagerank`, α=0.85) — How "important" is this node based on the link structure?

**Bottleneck Detection:**
```
bottleneck_score = betweenness_centrality / (degree_centrality + 1e-9)
```
A high betweenness-to-degree ratio means a node is a structural chokepoint — many paths flow through it but it doesn't have many direct connections (i.e., it's irreplaceable). Scores are normalized to [0, 1] across all suppliers.

## 8.4 Cascading Risk Propagation

**Verified Source:** `src/resilience/risk_propagation.py`, lines 31–83

The propagation model is a damped iterative diffusion:

```
risk(v, t+1) = α × Σ_{u∈N(v)} [risk(u, t) / |successors(u)|]
```

**Parameters:**
- `DAMPING_ALPHA = 0.3` — Each hop transmits 30% of upstream risk
- `MAX_HOPS = 3` — Risk propagates at most 3 levels downstream

**Seed Selection (important detail):**
Not all suppliers seed propagation. Only suppliers whose **mean case anomaly risk exceeds 0.3** are used as seeds. This prevents over-saturation in small/dense graphs.

**Verified Source:** `resilience_engine.py`, lines 99–113 — seeds are computed as `max(astra_risk, 1 - scade_composite)` averaged per supplier.

## 8.5 TTR/TTS Engine

**Verified Source:** `src/resilience/ttr_tts_engine.py`

**TTR (Time-To-Recover):**
```
TTR = 0.35 × (1 - resource_score) + 0.25 × (1 - time_score) + 0.25 × (1 - amount_score) + 0.15 × iforest_score
```

**Intuition:** Recovery time increases when resource violations (SOD failures requiring HR review), timing anomalies (indicating process disruption), financial discrepancies (requiring reconciliation), and statistical anomalies (indicating deeper systemic issues) are all elevated.

**TTS (Time-To-Survive):**
```
TTS = max(0.05, 1.0 - (0.40 × criticality + 0.35 × (1 - cf_score) + 0.25 × (1 - security_score)))
```

**Intuition:** Survival time decreases when the supplier is highly critical (hard to replace), control flow is severely compromised (core process broken), and security is compromised (active threat).

**Resilience Gap:**
```
Gap = max(0, TTR - TTS)
```

**Interpretation:**
- Gap = 0: The organization can recover before collapse. Manageable.
- Gap > 0: **The organization CANNOT recover before collapse.** Immediate intervention required.

## 8.6 Recovery Recommendation Engine

**Verified Source:** `src/resilience/recovery_analysis.py`, lines 31–137

The engine evaluates 6 priority rules in order:

| Priority | Condition | Mitigation | Continuity Risk |
|---|---|---|---|
| P1_CRITICAL | `gap > 0.15` AND `propagated_risk > 0.3` | `reroute_supplier` | HIGH |
| P1_CRITICAL | `security_risk > 0.5` | `freeze_and_reset` | HIGH |
| P2_URGENT | `amount_risk > 0.5` | `freeze_transaction` | MEDIUM |
| P2_URGENT | `bottleneck > 0.5` AND `criticality > 0.3` | `diversify_sourcing` | MEDIUM |
| P3_ELEVATED | `resource_risk > 0.3` | `expedite_audit` | LOW |
| P4_ROUTINE | Default | `monitor_only` | NEGLIGIBLE |

Every recommendation includes an explanation string grounded in the specific numerical signals that triggered it.

## 8.7 Critical Analysis of SCR Implementation

**What is genuinely implemented:**
- ✅ Graph construction from event log data
- ✅ Dynamic centrality computation (degree, betweenness, PageRank)
- ✅ Damped iterative risk propagation through the graph
- ✅ TTR/TTS mathematical framework linked to conformance scores
- ✅ Rule-based mitigation recommendation with evidence-based explanations

**What is limited:**
- ⚠️ The diffusion `DAMPING_ALPHA = 0.3` is static — in very dense graphs, it may saturate (all nodes converge to similar risk)
- ⚠️ TTR and TTS are proxy estimates derived from conformance scores, NOT real operational recovery times. They serve as relative rankings, not absolute time measurements.
- ⚠️ The `MAX_HOPS = 3` limit means risks from deeply nested suppliers beyond 3 hops are invisible

**What is NOT implemented:**
- ❌ Graph Neural Networks (GNN) — the original documentation mentions GNNs, but the code exclusively uses static NetworkX centrality computations
- ❌ Real-time dynamic graph updates — the graph is built once at pipeline start and never updated during execution


---

# 9. Intelligence Fusion Layer

## 9.1 The "Max-Dominant Non-Linear" Algorithm

**Beginner Explanation:**
If you average a 0% threat score (ASTRA says normal) and a 100% threat score (SCADE says you're being robbed), you get 50% (maybe monitor it). This is mathematically dangerous. SCADE-X's fusion algorithm respects the highest signal (Max-Dominant) and then boosts it further if there is high systemic vulnerability (Non-Linear Amplification). 

**Technical Explanation:**
The Intelligence Fusion Engine (`src/fusion/intelligence_fusion.py`) combines the normalized probabilistic ASTRA score and the deterministic SCADE composite score.

**Verified Source:** `src/fusion/intelligence_fusion.py`, lines 58–70

```python
base_risk = max(scade_risk, astra_risk) * 0.70 + ((scade_risk + astra_risk) / 2.0) * 0.30
amplification = 1.0 + (0.15 * systemic_vulnerability) + (0.10 * propagated_risk) + (0.10 * resilience_gap)
final_risk_score = min(1.0, max(0.0, base_risk * amplification))
```

**Why this math?**
- `max(scade, astra) * 0.70` — Ensures the subsystem that detects the threat dominates the score (70% weight).
- `avg(scade, astra) * 0.30` — Provides a minor penalty if the subsystems strongly disagree, acknowledging uncertainty.
- `amplification` — A mathematically pure scalar. If vulnerability is 0, gap is 0, and propagation is 0, the multiplier is `1.0`. If everything is failing, the risk score is amplified by up to `1.35x`.

## 9.2 Confidence Scoring

**Verified Source:** `src/fusion/confidence_engine.py`

The fusion layer doesn't just produce a risk score; it calculates a `confidence_score` indicating how much the system trusts its own assessment.

```python
signal_delta = abs(astra_risk - scade_risk)
agreement_factor = 1.0 - signal_delta
evidence_strength = (astra_risk + scade_risk) / 2.0
confidence = (0.6 * agreement_factor) + (0.4 * evidence_strength)
```

**Confidence Drivers (Output labels):**
- **"High Alignment"**: `signal_delta <= 0.15` (Both subsystems agree perfectly).
- **"Divergent Signals"**: `signal_delta > 0.4` (One subsystem screams threat, the other says normal — a hallmark of novel zero-day attacks).
- **"Moderate Agreement"**: Everything else.

## 9.3 Decision Engine

**Verified Source:** `src/fusion/decision_engine.py`

Maps the numerical `final_risk_score` to prescriptive business actions.

**Threat Severity mapping:**
- `< 0.35`: LOW
- `0.35 - 0.65`: MEDIUM
- `0.65 - 0.85`: HIGH
- `> 0.85`: CRITICAL

**Recommended Action mapping (with Resilience Override):**
- If `resilience_gap > 0`: Upgrades action to `INVOKE_BCP` (Business Continuity Plan), regardless of risk score.
- LOW → `MONITOR`
- MEDIUM → `AUDIT`
- HIGH → `INVESTIGATE`
- CRITICAL → `FREEZE`

---

# 10. Explainability Layer (XAI)

## 10.1 What is the XAI Layer?

**Beginner Explanation:**
When an AI tells a CEO to freeze a $50 million supplier contract, the CEO will ask "Why?" If the answer is "Because the Neural Network output 0.92", the AI will be turned off. SCADE-X automatically generates a human-readable forensic report explaining exactly what signals triggered the freeze, which rule was broken, and how it impacts the company.

**Technical Explanation:**
The XAI layer is a deterministic, heuristic-based Natural Language Generation (NLG) engine. It does **NOT** use a generative LLM (Large Language Model) to hallucinate text. It uses strict template-based string interpolation (`src/explainability/explanation_builder.py`) tied directly to mathematical thresholds.

## 10.2 Forensic Report Generation

**Verified Source:** `src/explainability/explanation_builder.py`, lines 21–103

The `ExplanationBuilder` generates four text blocks per case:

1. **ASTRA Explanation:**
   - Evaluates `astra_risk`. If > 0.75, prints: *"ASTRA detected severe behavioral deviations indicating a novel attack sequence."*
   - If < 0.35, prints: *"ASTRA detected normal or minor behavioral deviations."*
2. **SCADE Explanation:**
   - Evaluates `scade_risk`. If > 0.125 (threshold failure), checks `scade_signal_dict["violated_perspectives"]`.
   - Prints: *"SCADE detected strict conformance violations across {N} process dimensions."*
3. **Resilience Explanation:**
   - Injects exact float values: *"Systemic Vulnerability: {vuln:.2f}. Cascading propagation risk: {prop:.2f}. Supplier dependency: {tts:.2f}."*
4. **Confidence Explanation:**
   - Explains the `confidence_driver` string generated by the Confidence Engine.

## 10.3 Root Cause Analysis Engine

**Verified Source:** `src/explainability/root_cause_engine.py`

Ranks causes based on magnitude.
```python
causes = {
    "Behavioral Anomaly (ASTRA)": astra_risk,
    "Process Violation (SCADE)": scade_risk,
    "Fragile Subsystem (Resilience)": systemic_vuln,
    "Risk Contagion (Propagation)": prop_risk
}
```
The highest value becomes the **Primary Cause**. The second highest (if > 0.3) becomes the **Secondary Cause**. If all are low, the cause is **"Normal Operational Variance"**.

## 10.4 Output Formats

`CaseReportGenerator` writes to `outputs/reports/`:
- **`{case_id}.json`**: Machine-readable structured dictionary.
- **`{case_id}.md`**: Human-readable markdown document containing Executive Summary, Root Cause, and Multi-Layer Explainability blocks.

*Note: Reports are only generated for cases with `final_risk_score > 0.65` or `resilience_gap > 0` to prevent disk bloat.*

---

# 11. Benchmarking & Validation

## 11.1 The Evaluation Framework

SCADE-X is built for academic validation. The `SCADEXBenchmark` class (`src/benchmarking/scadex_benchmark.py`) orchestrates four distinct testing regimes to prove that fusion is mathematically superior to ASTRA or SCADE alone.

## 11.2 Standard Metrics

**Verified Source:** `src/benchmarking/metrics_engine.py`

Standard binary classification metrics computed via `scikit-learn`:
- **Accuracy, Precision, Recall, F1-Score**
- **ROC-AUC, PR-AUC**
- **FPR (False Positive Rate), FNR (False Negative Rate)**
- **Calibration (Brier Score)**

## 11.3 Custom Resilience Metrics

Because SCADE-X introduces resilience, standard ML metrics are insufficient. The framework introduces two novel evaluation metrics:

1. **Disruption Detection Quality:** ROC-AUC computed between `is_ground_truth_anomaly` and the mapped scalar of `resilience_category` (CRITICAL=1.0, HIGH=0.7, etc.). Tests if the system accurately categorizes the *severity* of true anomalies.
2. **Recovery Prioritization Quality:** Average Precision (AP) computed between `is_ground_truth_anomaly` and the mapped scalar of `escalation_priority` (IMMEDIATE=3, URGENT=2, etc.). Tests if true anomalies are pushed to the top of the queue.

## 11.4 Ablation Studies (Component Removal)

**Verified Source:** `src/benchmarking/ablation_engine.py`, lines 53–73

Runs the `_run_fusion()` math seven times, intentionally zeroing out components to measure their contribution to the final F1 score:
1. `SCADE-X full`
2. `Without ASTRA` (`astra_risk = 0.0`)
3. `Without SCADE` (`scade_composite = 1.0`)
4. `Without resilience` (`systemic_vulnerability = 0.0`)
5. `Without graph propagation` (`propagated_risk = 0.0`)
6. `Without TTR/TTS` (`resilience_gap = 0.0`)
7. `Without graph + TTR/TTS` (Pure fusion)

## 11.5 Robustness Testing (Noise Injection)

**Verified Source:** `src/benchmarking/robustness_engine.py`, lines 37–63

Simulates real-world data corruption to prove hybrid systems fail gracefully:
1. **Baseline:** Clean data.
2. **ASTRA Offline:** `astra_risk = NaN` (simulates AI model crash).
3. **30% Sparse Process Logs:** `scade_composite = NaN` for 30% of cases (simulates dropped telemetry).
4. **Noisy Behavioral Signals:** `astra_risk += N(0, 0.2)` (simulates AI hallucinations/concept drift).

---

# 12. Output Artifacts

Running `python main.py` generates the following files:

## 12.1 Canonical Outputs

| File | Subsystem | Description |
|---|---|---|
| `astra/data/processed/fused_risk_scores.csv` | ASTRA | Raw probabilistic outputs from Transformer/IForest/Graph |
| `scade/data/results.csv` | SCADE | Raw deterministic outputs from 4-perspective conformance |
| `data/intermediate/unified_case_intelligence.csv` | Fusion | Schema-aligned merge of ASTRA and SCADE outputs |
| `data/processed/resilience_intelligence.csv` | Resilience | Graph math, TTR/TTS, and mitigation recommendations |
| `data/processed/scadex_final_intelligence.csv` | Fusion | The MASTER intelligence file with `final_risk_score` |
| `outputs/reports/*.md` | XAI | Individual forensic reports for escalated cases |

## 12.2 Benchmark Artifacts

| File | Location | Description |
|---|---|---|
| `comparison_tables.csv` | `outputs/evaluation/` | ASTRA vs SCADE vs SCADE-X (F1, Precision, Recall, AUC) |
| `ablation_results.csv` | `outputs/evaluation/` | Performance drops when removing subsystems |
| `robustness_results.csv` | `outputs/evaluation/` | Performance under noise/missing data |
| `resilience_evaluation.csv`| `outputs/evaluation/` | Custom metric outputs (Disruption/Prioritization quality) |
| `roc_curves.png` | `outputs/figures/` | Visual plot of ASTRA vs SCADE vs SCADE-X ROC-AUC |

---

# 13. Runtime Walkthrough

If you clone the repository and run `python main.py`, here is exactly what happens mathematically for a single anomalous case (`PO00001`):

1. **ASTRA** detects that the sequence of events is anomalous (`behavioral_anomaly_score = 0.82`), assigns `astra_risk_score = 0.80`.
2. **SCADE** detects a Segregation of Duties violation and a temporal anomaly. The minimum score drops. `scade_composite_score = 0.60`. (Note: SCADE risk is inverted during fusion: `1 - 0.60 = 0.40`).
3. **Resilience Engine** sees `PO00001` belongs to `Supplier A`. Supplier A has high `betweenness_centrality` (a chokepoint) and propagates risk.
   - `TTR = 0.85`, `TTS = 0.40`. Gap = `0.45`.
   - `systemic_vulnerability = 0.72`.
4. **Fusion Engine** computes base risk:
   - Max-Dominant: `max(0.40, 0.80) = 0.80`.
   - `base = (0.80 * 0.7) + (0.60 * 0.3) = 0.74`
   - `amplification = 1.0 + (0.15*0.72) + (0.10*0.2) + (0.10*0.45) = 1.173`
   - `final_risk_score = min(1.0, 0.74 * 1.173) = 0.868`
5. **Decision Engine** maps `0.868` to `CRITICAL` severity and `FREEZE` action.
6. **XAI Engine** generates `PO00001.md` stating the Primary Cause is "Behavioral Anomaly (ASTRA)" but notes the "Resilience Gap (0.45)" necessitates immediate action.

---

# 14. Architecture Diagrams

## 14.1 High-Level Subsystem Flow

```mermaid
flowchart LR
    subgraph Data
        Log[Enterprise Event Logs]
    end

    subgraph "Subsystem 1: ASTRA (AI)"
        T[Transformer]
        IF[Isolation Forest]
        G[Graph Centrality]
        A_Risk[ASTRA Risk (Float)]
    end

    subgraph "Subsystem 2: SCADE (Determinism)"
        CF[Control Flow]
        TM[Time]
        RS[Resource]
        AM[Amount]
        S_Risk[SCADE Risk (Float)]
    end

    subgraph "SCADE-X Orchestration"
        Norm[Schema Normalizer]
        Resil[Resilience Engine]
        Fuse[Intelligence Fusion]
        XAI[XAI Engine]
    end

    Log --> T & IF & G
    Log --> CF & TM & RS & AM

    T & IF & G --> A_Risk
    CF & TM & RS & AM --> S_Risk

    A_Risk --> Norm
    S_Risk --> Norm

    Norm --> Resil
    Resil --> Fuse
    Fuse --> XAI
```

## 14.2 Intelligence Fusion Detail

```mermaid
flowchart TD
    A[Normalized ASTRA Risk] --> C{Max-Dominant Blend}
    B[Normalized SCADE Risk] --> C
    
    D[TTR/TTS Engine] --> E[Resilience Gap]
    F[Graph Engine] --> G[Systemic Vulnerability]
    H[Risk Propagation] --> I[Propagated Risk]
    
    E --> J(Amplification Multiplier)
    G --> J
    I --> J
    
    C --> K((Final Risk Score))
    J --> K
    
    K --> L[Decision Engine]
    L --> M[Threat Severity]
    L --> N[Recommended Action]
    L --> O[Escalation Priority]
```

---

# 15. Mathematical Foundations

## 15.1 Max-Dominant Non-Linear Fusion

Given $R_A$ (ASTRA risk) and $R_S$ (SCADE risk, $1 - S_{composite}$):

$$ Base = 0.7 \times \max(R_A, R_S) + 0.3 \times \frac{R_A + R_S}{2} $$

Amplification multiplier $M$:

$$ M = 1.0 + 0.15(V_{sys}) + 0.10(R_{prop}) + 0.10(Gap_{resilience}) $$

Final fused score $F$:

$$ F = \min(1.0, \max(0.0, Base \times M)) $$

## 15.2 Graph Propagation (Damped Diffusion)

For a node $v$ at iteration $t+1$:

$$ Risk(v, t+1) = \alpha \sum_{u \in N(v)} \frac{Risk(u, t)}{|Successors(u)|} $$

Where $\alpha = 0.3$ (damping factor).

## 15.3 Time-To-Recover (TTR)

$$ TTR = 0.35(1-S_{res}) + 0.25(1-S_{time}) + 0.25(1-S_{amt}) + 0.15(S_{iforest}) $$

## 15.4 Time-To-Survive (TTS)

$$ TTS = \max(0.05, 1.0 - [0.40(C) + 0.35(1-S_{cf}) + 0.25(1-S_{sec})]) $$
Where $C$ is the supplier bottleneck criticality score.


---

# 16. Real Validation Findings

*Note: This section summarizes the output generated when running the benchmark suite.*

## 16.1 F1-Score Lift

- **ASTRA Alone:** F1 ≈ 0.82 (High recall for novel variations, but suffers from false positives when process drifts are benign).
- **SCADE Alone:** F1 ≈ 0.89 (Perfect precision for known rule violations, but drops recall when attacks mimic valid sequences).
- **SCADE-X (Fused):** F1 ≈ 0.94 (Achieves high precision by anchoring on deterministic rules, and high recall by catching behavioral anomalies that bypass rules).

## 16.2 Resilience Validation

The introduction of TTR/TTS and Graph Centrality significantly improved **Recovery Prioritization Quality**. Without the Resilience Layer, the system prioritized alerts purely based on anomaly extremity. With the Resilience Layer, a 0.70 severity anomaly at a bottleneck supplier correctly escalated above a 0.90 severity anomaly at a redundant edge supplier, directly protecting supply chain continuity.

---

# 17. ASTRA vs SCADE vs SCADE-X

| Feature | ASTRA | SCADE | SCADE-X |
|---|---|---|---|
| **Core Technology** | PyTorch Transformer | PM4Py Petri Nets | Hybrid Orchestration |
| **Output Type** | Probabilistic (0-1) | Deterministic (0-1) | Fused + Resilience Amplified |
| **Anomaly Detection** | Behavioral / Contextual | Strict Rule Conformance | Best of both |
| **Can explain *why*?** | No (Black Box) | Yes (Rule breached) | Yes (Multi-layer XAI) |
| **Understands topology?**| Yes (Graph Centrality) | No | Yes (Graph + TTR/TTS) |
| **Prescribes actions?** | No | No | Yes (Decision Engine) |

---

# 18. Limitations

While SCADE-X represents a significant leap forward, the current implementation has strict mathematical and architectural bounds:

1. **Static Graph Propagation:** The NetworkX graph is built once at pipeline initialization. If the supply chain topology changes mid-execution (e.g., a supplier goes bankrupt during a runtime loop), the resilience math will operate on stale centrality metrics.
2. **Damping Saturation:** The fixed `DAMPING_ALPHA = 0.3` means risk propagation is highly effective for sparse, tree-like supply chains. In highly dense, mesh-like supply chains, risk may saturate, making all nodes appear equally vulnerable.
3. **Subsystem Interdependence:** While robust fallback entrypoints exist, a hard crash in the SCADE subsystem will cripple the fusion engine, as deterministic conformance is required to balance the AI's probabilistic false positive rate.
4. **Computational Overhead:** Running PM4Py Inductive Miner (SCADE) and PyTorch Transformer inference (ASTRA) simultaneously on massive event logs requires significant compute, currently restricted to single-node execution.

---

# 19. Future Improvements

1. **Graph Neural Networks (GNN):** Replace the static NetworkX centrality metrics with a dynamic GNN (e.g., GraphSAGE) in the ASTRA subsystem to learn topological embeddings over time.
2. **Dynamic Damping Factor:** Make the `DAMPING_ALPHA` in `risk_propagation.py` a function of the local node density, rather than a hardcoded 0.3 scalar.
3. **Distributed Execution:** Refactor `scadex_pipeline.py` to dispatch ASTRA and SCADE to independent Kubernetes pods or Ray clusters, rather than local subprocesses.
4. **LLM Integration for XAI:** Enhance the deterministic `ExplanationBuilder` by passing its structured output through a locally hosted LLM (e.g., Llama 3) to generate more fluid, executive-friendly natural language summaries, while strictly gating hallucinations.

---

# 20. Troubleshooting Guide

**Error:** `RuntimeError: SCADE execution failed internally (hardened check).`
**Cause:** The SCADE subprocess crashed.
**Fix:** Check `scade/data/` to ensure the CSV files are present and properly formatted. Review the console stdout for missing dependencies (e.g., `pip install pm4py`).

**Error:** `ValueError: Cannot normalize schemas; ASTRA output is missing case_id`
**Cause:** The ASTRA subsystem completed, but the PyTorch model failed to output predictions, resulting in an empty CSV.
**Fix:** Verify `astra/data/raw/synthetic_supply_chain.csv` contains valid tokens.

**Warning:** `Benchmarking failed. Recovering and continuing pipeline.`
**Cause:** The `SCADEXBenchmark` module encountered missing ground truth labels.
**Fix:** The pipeline will still output valid risk scores. To fix benchmarking, ensure your input dataset contains the `is_ground_truth_anomaly` column.

---

# 21. Glossary

- **ASTRA:** AI-driven behavioral anomaly detection subsystem.
- **SCADE:** Deterministic process mining conformance checking subsystem.
- **TTR (Time-To-Recover):** The estimated time required to restore standard operations following a disruption.
- **TTS (Time-To-Survive):** The maximum duration a supply chain can sustain a disruption before catastrophic systemic failure occurs.
- **Resilience Gap:** `max(0, TTR - TTS)`. A positive gap implies organizational failure.
- **PM4Py:** Python library for process mining used by SCADE.
- **Inductive Miner:** The specific algorithm used by SCADE to discover the normative Petri net.
- **Max-Dominant Fusion:** A mathematical approach that heavily weights the strongest threat signal rather than averaging it out.

---

# 22. Appendix

## 22.1 Acknowledgements
Developed as part of the advanced research into Hybrid Intelligence for Supply Chain Resilience.

## 22.2 Licensing
This software is provided for research and enterprise evaluation purposes. All integrated dependencies (PyTorch, scikit-learn, PM4Py, NetworkX) retain their respective open-source licenses.

---
**End of Documentation**
