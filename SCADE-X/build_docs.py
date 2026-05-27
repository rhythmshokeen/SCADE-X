    import datetime
import os

docs_dir = "docs"
output_md = os.path.join(docs_dir, "SCADE_X_COMPLETE_DOCUMENTATION.md")

sections = []

# 1. Cover Page
sections.append(f"""---
title: "SCADE-X: A Unified AI and Process Mining Framework for Supply Chain Resilience"
subtitle: "Complete Technical Documentation & System Reference"
author: "SCADE-X Engineering & Research Team"
date: "{datetime.datetime.now().strftime('%B %d, %Y')}"
version: "1.0.0"
---

\\newpage

# 1. Cover Page

**Project Title:** SCADE-X  
**Expanded Name:** Supply Chain Anomaly Detection & Engineering - Extended  
**Tagline:** Bridging Probabilistic Intelligence and Deterministic Conformance for Systemic Resilience  
**System Description:** SCADE-X is an enterprise-grade, hybrid intelligence platform. It fuses Transformer-driven behavioral anomaly detection (ASTRA), PM4Py-driven control-flow process mining (SCADE), and a kinetic cascading-risk Supply Chain Resilience (SCR) engine into a singular unified execution pipeline.  
**Generated Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Version:** v1.0.0 (Research Release)

\\newpage
""")

# 2. Executive Summary
sections.append("""
# 2. Executive Summary

Global supply chains are exceptionally fragile. Modern enterprises struggle not only with detecting isolated fraudulent transactions but understanding how those isolated failures compound into catastrophic, systemic supply chain breakdowns. 

SCADE-X solves this fundamental limitation.

It exists to bridge a persistent gap in modern computational intelligence: the divide between deep learning anomaly detection (which identifies odd behavior without explaining the business rules violated) and process mining (which flags strict rule violations without understanding the nuanced intent or behavioral context). 

By combining **ASTRA** (an AI-driven behavioral modeling subsystem) and **SCADE** (a deterministic process mining and conformance checking subsystem) under a unified **Supply Chain Resilience (SCR) Intelligence Layer**, SCADE-X provides unprecedented visibility into operational fragility.

What makes SCADE-X fundamentally different is its kinetic modeling of risk. It does not treat anomalies as static dots on a scatter plot. Instead, utilizing advanced Graph Centrality and Damped Iterative Diffusion, SCADE-X maps how an anomaly at one supplier cascades downstream, estimating exact Time To Recover (TTR) and Time To Survive (TTS) windows. 

**Core Outcomes:**
- **Zero-Day Anomaly Detection**: Unsupervised identification of novel fraud topologies.
- **Strict Conformance Enforcement**: Rigid evaluation of Temporal, Resource, Amount, and Control-Flow bounds.
- **Resilience Profiling**: Identification of structural bottlenecks and single-points-of-failure.
- **Actionable Forensics**: Explainable, human-readable root cause reports designed for auditors, circumventing the traditional black-box dilemma of AI systems.

\\newpage
""")

# 3. Project Motivation
sections.append("""
# 3. Project Motivation

The inception of SCADE-X stems from the critical failures of single-paradigm risk architectures observed in global procurement and logistics operations.

## The Fraud Detection Limitation
Traditional fraud detection heavily relies on rule-based Expert Systems or simple statistical thresholds. These systems break under the natural agility required by modern supply chains. They generate massive False Positive avalanches when procurement teams legitimately alter processes to adapt to global constraints.

## The Supply Chain Vulnerability
Supply chains are directed, interconnected graphs. If a Tier-3 supplier is compromised, the disruption propagates. Current systems fail to model this kinetic propagation. An anomaly of severity 'Low' at an isolated edge node is fundamentally different from a severity 'Low' anomaly at a structural chokepoint bridging two massive procurement communities. Standard detection engines are entirely blind to this topology.

## Why Process Mining Alone is Insufficient
Process mining tools (like Celonis or raw PM4Py) rigorously extract and enforce process maps. If a Purchase Order skips an 'Approve' step, it is flagged. However, deterministic process mining lacks behavioral context. A malicious insider perfectly executing a duplicated payment process will pass all process mining checks because the structural *sequence* of events is technically valid, even if the underlying *behavior* is adversarial.

## Why AI Alone is Insufficient
Deep learning models (like Transformers and Isolation Forests) detect latent, complex patterns of adversarial behavior. However, they are inherent black-boxes. An AI model flagging a transaction as 98% anomalous is practically useless to a compliance auditor if it cannot explicitly state which Segregation-of-Duties (SOD) law was violated.

## The Hybrid Intelligence Necessity
SCADE-X is built on the philosophy of Hybrid Intelligence. It leverages AI to understand latent behavior (ASTRA) and uses Process Mining to ground that behavior in deterministic, auditable reality (SCADE). The synthesis of these two signals, mathematically amplified by physical network resilience, represents the bleeding edge of operational intelligence.

\\newpage
""")

# 4. What is SCADE-X?
sections.append("""
# 4. What is SCADE-X?

In simple terms, SCADE-X is an automated security and compliance brain for supply chain logistics. It watches every transaction, purchase order, and shipment. It learns what "normal" looks like, flags when things look suspicious, checks if strict company rules were broken, and calculates exactly how much danger the entire supply chain is in if that specific supplier fails.

Technically, SCADE-X is an orchestration ecosystem wrapping three major technological domains:

1. **AI Intelligence (ASTRA)**: A latent behavioral anomaly detection framework utilizing NLP-style Sequence Modeling (Transformers) and structural anomaly isolation (Isolation Forests) to score the probabilistic risk of individual cases.
2. **Process Mining (SCADE)**: A deterministic conformance checker leveraging the Inductive Miner and Token-Based Replay algorithms to quantify exact rule breakage across Control-Flow, Temporal drift, Amount boundaries, and Resource (SOD) assignments.
3. **Resilience Intelligence (SCR)**: A graph-theoretical vulnerability engine. It models the entire supply chain as a `NetworkX` directed graph, computes structural bottleneck scores, and cascades localized anomalies through the network via a damped iterative diffusion algorithm.

These three domains are bound together by:
- **Schema Normalization**: A layer that dynamically aligns discordant subsystem outputs into a singular canonical intelligence matrix.
- **Intelligence Fusion**: A non-linear decision engine that merges probabilistic risk, deterministic failure, and systemic resilience into a final `final_risk_score`.
- **Explainability Engine (XAI)**: A forensic text-generation layer translating complex floating-point metrics into readable executive markdown reports.
- **Benchmarking Engine**: An automated scientific validation layer capable of running ablation studies and calculating standard ML robustness metrics (ROC-AUC, Precision/Recall) against ground-truth labels.

\\newpage
""")

# 5. System Architecture
sections.append("""
# 5. System Architecture (Deep Dive)

SCADE-X operates on an "Outside-In" Orchestration pattern. It treats ASTRA and SCADE as isolated, immutable microservices, shielding memory spaces and dependencies via subprocess sandboxing.

## Complete System Architecture Diagram

```mermaid
graph TD
    A[Raw Supply Chain Logs] --> B(ASTRA Subsystem)
    A --> C(SCADE Subsystem)
    
    subgraph ASTRA [ASTRA: Behavioral Intelligence]
        B1[Feature Engineering] --> B2[Transformer Sequence Model]
        B1 --> B3[Isolation Forest]
        B1 --> B4[Graph Centrality]
        B2 --> B_Fusion[ASTRA Fusion]
        B3 --> B_Fusion
        B4 --> B_Fusion
    end
    B --> ASTRA
    B_Fusion --> D(Schema Normalizer)

    subgraph SCADE [SCADE: Process Mining Intelligence]
        C1[PM4Py Inductive Miner] --> C2[Control Flow Replay]
        C1 --> C3[Temporal Analysis]
        C1 --> C4[Resource / SOD Checks]
        C1 --> C5[Amount & Security]
        C2 --> C_Fusion[SCADE Composite]
        C3 --> C_Fusion
        C4 --> C_Fusion
        C5 --> C_Fusion
    end
    C --> SCADE
    C_Fusion --> D

    D --> E(Resilience Intelligence Layer)
    
    subgraph SCR [Supply Chain Resilience]
        E1[NetworkX Graph Metrics] --> E2[Cascading Risk Propagation]
        E3[TTR / TTS Calculation] --> E4[Operational Fragility]
        E2 --> E4
        E4 --> E_Rec[Recovery Engine]
    end
    E --> SCR
    
    E_Rec --> F(Hybrid Risk-Aware Fusion)
    
    F --> G(Explainability Layer XAI)
    G --> H(Final Decision Outputs)
```

## Step-by-Step Execution Pipeline

Executing `python main.py` initiates the `SCADEXUnifiedPipeline`, governed by the `RuntimeManager`. The strict chronological flow is:

1. **Validation**: The orchestrator verifies that required configuration files (`configs/scadex_config.yaml`) and target data files exist.
2. **ASTRA Execution**: Invoked via `astra_runner.py` in a sterile subprocess. Reads `synthetic_supply_chain.csv` and generates `fused_risk_scores.csv` and `supply_chain_graph.gpickle`.
3. **SCADE Execution**: Invoked via `scade_runner.py` in a sterile subprocess. Processes raw logs through Inductive Mining, evaluates multi-perspective conformance, and produces `results.csv`.
4. **Schema Normalization**: `schema_normalizer.py` ingests both CSVs. It maps differing schema semantics (e.g., standardizing Case IDs from `PO-0001` to `PO00001`) and applies outer-join imputation, resulting in `unified_case_intelligence.csv`.
5. **Resilience Intelligence**: `resilience_engine.py` constructs the supply chain graph, computes node centrality, cascades anomaly risks via diffusion, evaluates TTR/TTS gaps, and prescribes structural recovery actions. Outputs to `resilience_intelligence.csv`.
6. **Intelligence Fusion**: `intelligence_fusion.py` blends the raw metrics and resilience modifiers into a singular `final_risk_score`, outputting `scadex_final_intelligence.csv`.
7. **Explainability Generation**: `xai_engine.py` reads the fused signals and programmatically drafts human-readable JSON/Markdown forensic reports for the highest-risk cases.
8. **Benchmarking**: `scadex_benchmark.py` compares the final outputs against synthetic ground-truth labels to compute model performance and robustness metrics.
9. **Artifact Export**: The orchestrator physically moves all generated artifacts (CSVs, Logs, MDs, JSONs) to the permanent user-facing `outputs/` directory structure.

\\newpage
""")

# 6. Folder Structure Deep Explanation
sections.append("""
# 6. Folder Structure Deep Explanation

The SCADE-X repository enforcing clean architectural separation of concerns.

```text
SCADE-X/
├── astra/                  # The isolated ASTRA deep learning subsystem
├── scade/                  # The isolated SCADE process mining subsystem
├── configs/                # Global orchestration configurations (scadex_config.yaml)
├── data/
│   ├── raw/                # Source logs (synthetic_supply_chain.csv)
│   ├── intermediate/       # Internal normalization artifacts
│   └── processed/          # Fusion and resilience dataframes
├── docs/                   # Markdown, Figures, and Documentation assets
├── outputs/                # User-facing terminal exports
│   ├── reports/            # XAI output files
│   ├── figures/            # Graphical plots (Benchmarking curves)
│   ├── logs/               # Execution logs from the RuntimeManager
│   ├── benchmark/          # Accuracy and ablation metrics
│   ├── resilience/         # Final resilience intelligence export
│   └── final_intelligence/ # The master decision matrix CSV
├── src/
│   ├── orchestration/      # Pipeline runners, config managers, loggers
│   ├── fusion/             # Schema normalizers, decision/confidence engines
│   ├── resilience/         # Graph math, TTR/TTS, cascading propagation
│   ├── explainability/     # Root cause forensics generators
│   └── benchmarking/       # ROC AUC, Precision/Recall, Ablation logic
└── main.py                 # Primary CLI Entry Point
```

**Key Modules:**
- `src/resilience/ttr_tts_engine.py`: Contains the complex mathematical estimators for survival and recovery windows.
- `src/fusion/intelligence_fusion.py`: Houses the non-linear hybrid fusion algorithm that mathematically merges subsystems.
- `src/orchestration/scadex_pipeline.py`: The master sequential control loop.

\\newpage
""")

# 7. ASTRA Deep Dive
sections.append("""
# 7. ASTRA Deep Dive

**ASTRA (AI-driven Supply Chain Threat & Risk Assessment)** serves as the probabilistic, latent intelligence brain of SCADE-X.

## Architecture & Operation
ASTRA transforms highly dimensional tabular event logs into sequence-based behavioral models.
- **Sequence Modeling (Transformers)**: ASTRA treats a supply chain case (e.g., a Purchase Order lifecycle) as a 'sentence'. It tokenizes activities (`CREATE_PO`, `APPROVE_PO`, `PAYMENT`) and trains a Transformer network to predict the next logical step. If a sequence deviates wildly from the learned probability distribution, it assigns a high behavioral risk score.
- **Isolation Forests**: Running in parallel, an Isolation Forest evaluates continuous features (Duration, Cost, Activity Counts). It isolates statistical outliers using random partitioning.
- **Static Graph Centrality**: ASTRA extracts the bipartite graph of cases and suppliers to pre-compute basic centrality, establishing the preliminary topological weight.

## Intelligence Generation
ASTRA fuses its internal signals into `astra_risk_score`. Its primary value to SCADE-X is detecting "zero-day" adversarial behaviors that conform to basic process rules but exhibit subtle, malicious statistical drift.

## Limitations
ASTRA cannot identify explicitly which business rule was violated. A high score means "this looks highly unusual based on historical distributions", but it lacks the deterministic vernacular required for legal compliance audits. This black-box limitation necessitates its pairing with SCADE.

\\newpage
""")

# 8. SCADE Deep Dive
sections.append("""
# 8. SCADE Deep Dive

**SCADE (Supply Chain Conformance and Anomaly Detection Engine)** provides the deterministic, audit-grade process intelligence for SCADE-X.

## Process Mining and PM4Py
SCADE heavily utilizes PM4Py (Process Mining for Python). Process mining is a discipline that extracts knowledge from event logs to automatically discover, monitor, and improve real processes.
- **Inductive Miner**: SCADE digests the event log to algorithmically "discover" the true baseline process model, generating a Petri Net that strictly defines parallel and sequential acceptable behaviors.
- **Token-Based Replay**: To evaluate anomalous cases, SCADE replays the case's event sequence through the Petri Net. If the trace requires "missing tokens" or leaves behind "remaining tokens", SCADE mathematically penalizes the `cf_score` (Control-Flow Score).

## Multi-Perspective Conformance
Beyond basic sequence checking, SCADE enforces rigorous constraints across four additional perspectives:
1. **Temporal Analysis**: Calculates Gaussian bounds ($\mu, \sigma$) for expected activity durations. Exceeding $2\sigma$ drift penalizes the `time_score`.
2. **Resource Analysis**: Enforces Segregation of Duties (SOD). If the same user executes both `CREATE_PO` and `APPROVE_PO`, the `resource_score` drops to 0.0.
3. **Amount Analysis**: Detects financial drift or duplicated payment executions, bounding the `amount_score`.
4. **Security Context**: Evaluates external SIEM (Security Information and Event Management) logs. If an activity aligns with an IP anomaly or failed login context, the `security_score` is depleted.

## The Fraud Signal
SCADE fuses these deterministic bounds into a `scade_composite_score`. A low score definitively proves a business rule was broken.

\\newpage
""")

# 9. Supply Chain Resilience Layer
sections.append("""
# 9. Supply Chain Resilience Layer (Extremely Detailed)

The Supply Chain Resilience (SCR) layer distinguishes SCADE-X from all preceding anomaly detection systems. It shifts the operational philosophy from identifying *that* a failure occurred to quantifying *how* that failure will systemically damage the network.

## Graph Centrality and Bottlenecks
The supply chain is a directed graph $G=(V, E)$. The resilience engine loads this topology to compute structural metrics using `NetworkX`:
- **Supplier Criticality ($C_D$)**: Driven by Degree Centrality. Suppliers heavily connected to numerous critical paths.
- **Bottleneck Score ($B$)**: Defined as Betweenness Centrality normalized by Degree Centrality. It identifies bridge nodes that, if disrupted, sever major communities within the supply chain.

## Cascading Risk Propagation
A disruption is not static. SCADE-X simulates the blast radius of anomalies utilizing a Damped Iterative Diffusion model. Let $r(v, t)$ be the risk at node $v$ at iteration $t$, seeded by the anomaly scores of compromised suppliers.
$$ r(v, t+1) = \\alpha \\sum_{u \\in N_{pre}(v)} \\frac{r(u, t)}{deg_{out}(u)} $$
With a damping factor of $\\alpha = 0.3$, the risk "bleeds" downstream, quantifying `propagated_risk` for cases that technically behave normally but are structurally doomed by an upstream failure.

## The Kinetics of Recovery: TTR and TTS
SCADE-X anchors on two kinetic metrics:
1. **Time To Recover (TTR)**: How long will it take to remediate the case? TTR scales dynamically based on the complexity of the failed perspective. Financial deviations and SOD violations incur heavy auditing delays.
   $$ TTR = 0.35(1 - S_{res}) + 0.25(1 - S_{time}) + 0.25(1 - S_{amt}) + 0.15 \\cdot R_{iforest} $$
2. **Time To Survive (TTS)**: How long before the anomaly causes a critical systemic failure? TTS shrinks drastically if the compromised supplier is highly critical and the security/control-flow boundaries are shattered.
   $$ TTS = \\max\\Big(0.05, \\ 1.0 - [0.40 \\cdot C_D(v) + 0.35(1 - S_{cf}) + 0.25(1 - S_{sec})]\\Big) $$

**The Resilience Gap**: Calculated as $\\max(0, TTR - TTS)$. If a system requires more time to recover than it has to survive, catastrophic failure is imminent.

## Prescriptive Mitigation Logic
The `recovery_analysis.py` engine translates these mathematical states into actionable business logic (`mitigation_strategy`, `recovery_priority`):
- **P1 CRITICAL / Reroute Supplier**: Triggered instantly if `Resilience Gap > 0.15` and `Propagated Risk > 0.3`.
- **P1 CRITICAL / Freeze & Reset**: Triggered if `Security Score < 0.5`.
- **P2 URGENT / Diversify Sourcing**: Triggered if a highly critical supplier exhibits a `Bottleneck Score > 0.5`.

\\newpage
""")

# 10. Intelligence Fusion Layer
sections.append("""
# 10. Intelligence Fusion Layer

The Intelligence Fusion Layer algorithmically merges the probabilistic ASTRA risk, deterministic SCADE failure, and SCR fragility metrics into a final, highly actionable intelligence signal.

## Base Risk vs Final Risk

SCADE-X explicitly isolates the underlying anomaly severity (`base_risk_score`) from the resilience-amplified threat severity (`final_risk_score`).

**1. Base Risk Calculation**:
The system employs a Max-Dominant Non-Linear blend. It prioritizes the "weakest link" (the most severe signal from either ASTRA or SCADE) but smooths it using the average to prevent single-signal false positive avalanches. Let $\\mathcal{S}_r = 1.0 - SCADE$ and $\\mathcal{A}_r = ASTRA$.
$$ R_{base} = 0.7 \\cdot \\max(\\mathcal{S}_r, \\mathcal{A}_r) + 0.3 \\cdot \\left(\\frac{\\mathcal{S}_r + \\mathcal{A}_r}{2}\\right) $$

**2. Resilience Amplification (Final Risk)**:
If an anomaly occurs at a structural bottleneck ($V_{sys}$), creates heavy downstream cascading risk ($P_{risk}$), or triggers a negative survival window ($Gap$), the base risk is mathematically amplified up to a systemic maximum.
$$ R_{final} = \\min\\Big(1.0, \\ R_{base} \\cdot (1.0 + 0.15 \\cdot V_{sys} + 0.10 \\cdot P_{risk} + 0.10 \\cdot Gap)\\Big) $$

**Real-World Example**:
A supplier experiences a minor temporal anomaly (Delivery delayed by 2 days). 
- **Scenario A (Non-Critical Edge Node)**: Base Risk is 0.30. Amplification is ~1.0. Final Risk is 0.30 (LOW). The engine recommends `MONITOR_ONLY`.
- **Scenario B (Critical Bottleneck Node)**: Base Risk is 0.30. Because the node is highly central and triggers cascading risk downstream, Amplification spikes to 1.30. Final Risk jumps to 0.39. While still moderate, the system now flags a `P2_URGENT` condition to `DIVERSIFY_SOURCING` to protect the network structure.

\\newpage
""")

# 11. Explainability Engine
sections.append("""
# 11. Explainability Engine (XAI)

The Explainability Engine is critical for executive adoption. Complex fusion mathematics must be translated into auditable, human-readable forensic reports.

The `xai_engine.py` programmatically filters the highest-risk cases ($R_{final} > 0.75$) and generates comprehensive Case Reports. 

Outputs are serialized in both `JSON` (for downstream API ingestion) and `Markdown` (for immediate human review). 

An XAI report explicitly details:
- **Primary Root Cause**: Translates the heaviest mathematical driver (e.g., $S_{res} = 0.0$) into text (e.g., "Severe Segregation of Duties Violation Detected").
- **Resilience Context**: Explains *why* the case is dangerous topologically ("Supplier sits at a critical graph bottleneck").
- **Prescriptive Action**: Suggests the optimal recovery path ("Initiate process isolation and compliance audit").

By providing the exact mathematical `contributing_signals` alongside the narrative, SCADE-X completely eliminates the opacity inherent to traditional AI anomaly detection.

\\newpage
""")

# 12. Benchmarking & Evaluation
sections.append("""
# 12. Benchmarking & Evaluation

SCADE-X is engineered for rigorous academic and enterprise validation. The Benchmarking framework automatically assesses the holistic performance of the pipeline against embedded synthetic ground truth labels (`is_ground_truth_anomaly`).

## Evaluation Methodology
The `metrics_engine.py` generates standard Machine Learning classification boundaries:
- **Accuracy, Precision, Recall, F1-Score**
- **ROC-AUC & PR-AUC**: For probabilistic evaluation of threshold independence.
- **False Positive / False Negative Rates**

## Ablation Testing
The core of the benchmarking suite is the Ablation Engine. It systematically masks out components of SCADE-X to scientifically prove their value.
- **Run 1**: Evaluates SCADE-X utilizing only ASTRA signals.
- **Run 2**: Evaluates SCADE-X utilizing only SCADE signals.
- **Run 3**: Evaluates SCADE-X full fusion *without* the Resilience Layer amplification.
- **Run 4**: Full SCADE-X deployment.

This methodology empirically proves how resilience metrics reduce False Positive fatigue for non-critical cases while elevating true structural threats.

\\newpage
""")

# 13. Outputs Produced by SCADE-X
sections.append("""
# 13. Outputs Produced by SCADE-X

SCADE-X generates an array of persistent artifacts in the `outputs/` directory.

| Directory / File | Type | Description |
| --- | --- | --- |
| `final_intelligence/scadex_final_intelligence.csv` | CSV | The master decision matrix containing fused scores, recommended actions, and base vs final risk comparisons. |
| `resilience/resilience_intelligence.csv` | CSV | The raw output of the SCR layer, detailing TTR/TTS, bottleneck metrics, and propagation per case. |
| `benchmark/scadex_benchmark.csv` | CSV | Classification metrics comparing ASTRA, SCADE, and SCADE-X. |
| `explanations/scadex_explanations.csv` | CSV | A tabular summary of the JSON root-cause text generation for rapid database ingestion. |
| `reports/case_report_*.md` | Markdown | Beautifully formatted forensic text documents explaining critical failures. |
| `reports/case_report_*.json` | JSON | Machine-readable equivalents of the forensic markdown files. |
| `figures/` | PNG/SVG | Matplotlib/Seaborn generated plots including ROC-AUC curves and Model Comparison bar charts. |
| `logs/scadex_pipeline_*.log` | Log | Highly verbose timestamped runtime execution logs detailing subprocess lifecycle and validation states. |

\\newpage
""")

# 14. Screenshot Placeholder Sections
sections.append("""
# 14. Interface & Artifact Screenshots

*The following section designates placeholders for formal documentation screenshots.*

**1. Successful Pipeline Execution (Terminal Output)**
[INSERT SCREENSHOT HERE]
* **Command:** `python main.py`
* **Expected Output:** The vibrant console log showing Stage 1 through 9 completing with durations, ending with "✅ SCADE-X Pipeline Execution Completed Successfully."
* **Context:** Demonstrates the end-to-end operational fluidity and speed of the orchestrator.

**2. SCADE Subsystem Detection Summary**
[INSERT SCREENSHOT HERE]
* **Command:** Internal `scade_runner.py` subprocess logs.
* **Expected Output:** Multi-Perspective Detection Summary table showing cases flagged across CF, Time, Resource, and Amount bounds.
* **Context:** Highlights the deterministic power of process mining before fusion.

**3. Final Intelligence Schema Output**
[INSERT SCREENSHOT HERE]
* **Path:** `outputs/final_intelligence/scadex_final_intelligence.csv` (viewed in Excel/Numbers)
* **Expected Output:** The tabular display of `base_risk_score`, `final_risk_score`, `resilience_category`, and `recommended_action`.
* **Context:** Demonstrates the comprehensive data contract delivered to upstream ERP/SIEM platforms.

**4. Explanability Engine Forensic Report**
[INSERT SCREENSHOT HERE]
* **Path:** `outputs/reports/case_report_PO-0025.md`
* **Expected Output:** The rendered Markdown forensic report containing Root Cause Analysis and Systemic Impact statements.
* **Context:** Showcases the executive-friendly translation of complex fusion math.

\\newpage
""")

# 15. Example Walkthrough
sections.append("""
# 15. Example Walkthrough: Case PO-0025

Let us trace a single transaction—Purchase Order `PO-0025`—through the SCADE-X pipeline to visualize the operational reality.

1. **Raw Input**: The case appears in `synthetic_supply_chain.csv` where an employee creates a PO, approves their own PO, and initiates payment to Supplier `SUP-006`.
2. **ASTRA Detection**: The Transformer model flags the sequence of activities as highly improbable ($A_{risk} = 0.88$).
3. **SCADE Detection**: PM4Py discovers a Segregation of Duties (SOD) violation because `CREATE_PO` and `APPROVE_PO` share the same user ID ($S_{res} = 0.0$). SCADE composite risk hits $1.0$.
4. **Resilience Analysis**: The Graph Engine notes `SUP-006` is highly central. The SOD violation spikes the TTR. The Resilience Gap is mathematically triggered ($TTR > TTS$).
5. **Risk Fusion**: The Max-Dominant logic recognizes the massive SCADE failure. Base risk is $0.96$. Due to the Resilience Gap and downstream propagation risk, the final score amplifies to $1.00$.
6. **Recommendation**: The Decision Engine maps the $S_{res}$ failure and the Resilience Gap to output: `P1_CRITICAL` → `PROCESS_ISOLATION`.
7. **Explainability**: The XAI engine generates `case_report_PO-0025.md`, stating: *"Severe Segregation of Duties Violation Detected. Supplier sits at a critical graph bottleneck. Initiate process isolation and compliance audit immediately."*

\\newpage
""")

# 16. Limitations
sections.append("""
# 16. Limitations

While SCADE-X represents a significant leap forward, it maintains several engineering limitations:

1. **Graph Saturation in Dense Networks**: The Damped Iterative Diffusion algorithm utilizes a static $\\alpha$ factor. In extremely dense or very small synthetic networks, risk propagates too rapidly, artificially saturating the downstream network and diminishing localized visibility.
2. **Computational Complexity of Control Flow**: Token-based replay in the SCADE subsystem scales linearly but heavily. For extremely massive, highly concurrent logs ($>10^7$ events), the Petri Net conformance checking will induce severe memory latency unless refactored for Apache Spark / Distributed environments.
3. **Heuristic Weighting**: The fusion parameters (e.g., the $0.7/0.3$ base split) and TTR/TTS coefficient weights are heuristically designed. They are mathematically sound but lack empirical hyperparameter optimization against decades of historical ERP failure logs.

\\newpage
""")

# 17. Future Improvements
sections.append("""
# 17. Future Improvements

The SCADE-X architecture is designed for continuous research extension:

1. **Graph Neural Networks (GNNs)**: Replacing the static NetworkX-driven Damped Iterative Diffusion model with learned GNN architectures. This would allow the system to inherently "learn" how risk cascades through distinct industries based on historical disruptions.
2. **LLM Integration for XAI**: Upgrading the Explainability Engine from programmatic template-mapping to secure, locally hosted Large Language Models (e.g., Llama 3) to dynamically query process maps and generate conversational forensic audits.
3. **Automated Recovery Execution**: Transitioning from prescribing `Recommended Actions` to automatically executing them via ERP APIs (e.g., automatically freezing a SAP vendor account dynamically upon $R_{final} > 0.90$).

\\newpage
""")

# 18. Glossary
sections.append("""
# 18. Glossary

- **ASTRA**: Artificial Intelligence Supply Chain Threat & Risk Assessment. The deep-learning behavioral subsystem.
- **SCADE**: Supply Chain Conformance and Anomaly Detection Engine. The deterministic process mining subsystem.
- **PM4Py**: Process Mining for Python. The core algorithmic library used in SCADE to generate Petri Nets.
- **Conformance Checking**: The act of comparing an observed real-world trace against a mathematically mandated process model to detect deviations.
- **TTR (Time To Recover)**: A metric defining the kinetic timeline required to manually or systemically remediate a specific disruption.
- **TTS (Time To Survive)**: A metric defining the window of time before a localized anomaly triggers catastrophic systemic failure across the supply chain.
- **Systemic Vulnerability**: The underlying structural fragility of a supply chain topology, independent of current anomalies.
- **Cascading Risk (Propagation)**: The diffusion of threat probability from an infected node downstream to reliant operations.

\\newpage
""")

# 19. Appendix
sections.append("""
# 19. Appendix

## Pipeline Execution Commands

**Standard Execution:**
```bash
python main.py
```

**Debug Execution (Verbose Logs):**
```bash
python main.py --debug
```

**Fast Execution (Skip Benchmarks):**
```bash
python main.py --skip-benchmark
```

## Essential Subsystem Paths

- `scadex_pipeline.py`: Main orchestrator execution loop.
- `intelligence_fusion.py`: Contains the `$R_{base}$` and `$R_{final}$` mathematical fusion logic.
- `resilience_engine.py`: Computes network graphs and iterates topological propagation.
- `ttr_tts_engine.py`: Defines the foundational kinetics for operational fragility.

## Mathematical Formulation Reference

**Resilience Gap:**
$$ Gap = \\max(0, TTR - TTS) $$

**Operational Fragility ($F$):**
$$ F = 0.30 \\cdot R_{ASTRA} + 0.40 \\cdot R_{SCADE} + 0.30 \\cdot \\left(\\frac{TTR}{TTR + TTS}\\right) $$
""")

# Write out the Markdown file
with open(output_md, "w") as f:
    f.write("\n".join(sections))

print("Markdown documentation generated successfully.")
