# SCADE-X: A Unified AI and Process Mining Framework for Supply Chain Resilience

## Abstract
Modern supply chains are highly complex and opaque networks vulnerable to cascading disruptions. Traditional anomaly detection relies on isolated, single-paradigm methods (either deterministic rules or black-box machine learning), failing to capture the systemic fragility of a network. We present SCADE-X, a hybrid framework unifying deep learning behavioral intelligence (ASTRA) with deterministic process mining (SCADE), integrated through a novel Supply Chain Resilience (SCR) engine. By mathematically formulating Time To Recover (TTR), Time To Survive (TTS), and cascading risk propagation over a NetworkX-based interaction graph, SCADE-X dynamically identifies structural bottlenecks and prevents catastrophic failures before they materialize.

## 1. Introduction
The fragility of global supply chains demands proactive intelligence. While deep learning models excel at identifying latent behavioral anomalies, they struggle with precise, process-aware compliance. Conversely, deterministic process mining algorithms identify strict control-flow deviations but lack the contextual intelligence to assess whether a deviation is a routine adaptation or a malicious exploit. SCADE-X solves this by treating anomalies not as isolated events, but as kinetic forces propagating through a supply chain graph.

## 2. Related Work
Existing process mining architectures (e.g., PM4Py) primarily focus on conformance checking. Deep learning approaches in this domain (e.g., Transformers, Isolation Forests) often treat sequence prediction in isolation. Supply chain resilience literature establishes the theoretical constructs of TTR and TTS, but rarely operationalizes them directly into an automated machine learning fusion pipeline. SCADE-X bridges these three domains into a single executable pipeline.

## 3. Methodology

### 3.1 System Architecture
SCADE-X is an orchestrator-driven pipeline incorporating independent subsystems converging via a schema normalizer into a resilience intelligence layer.

### 3.2 ASTRA Subsystem (Behavioral Intelligence)
Utilizes Transformer-based sequential modeling alongside Isolation Forests to establish a probabilistic baseline of expected supplier behavior.

### 3.3 SCADE Subsystem (Process Intelligence)
Leverages Inductive Miner and Token-Based Replay to enforce strict bounds on control flow, temporal expectations, and segregation-of-duties (SOD).

### 3.4 Supply Chain Resilience Layer (SCR)
The SCR layer shifts focus from anomaly *detection* to disruption *impact*:
- **Graph Centrality**: Models the network utilizing NetworkX to compute structural bottlenecks.
- **Risk Propagation**: Uses a damped iterative diffusion model ($ \alpha = 0.3 $) to simulate how risk propagates from compromised suppliers downstream.
- **TTR / TTS Engine**: Mathematically estimates survival and recovery windows based on process conformance and supplier criticality. A positive Resilience Gap ($TTR > TTS$) serves as an absolute indicator of impending catastrophic failure.

### 3.5 Hybrid Risk-Aware Fusion
A non-linear, max-dominant fusion engine that merges normalized scores, significantly amplified by resilience vulnerabilities.

## 4. Experimental Setup
The system is evaluated on a synthetic multi-perspective procurement dataset representing P2P (Procure-to-Pay) traces with embedded control flow violations, temporal drift, and cascading supplier failures.

## 5. Results & Discussion
Ablation studies demonstrate that the inclusion of the SCR layer (specifically the resilience gap and cascading propagation multipliers) drastically reduces false positive fatigue for non-critical anomalies, while correctly escalating otherwise "moderate" anomalies occurring at structural graph bottlenecks.

## 6. Limitations
The cascading risk model is highly sensitive to graph density. In sparsely connected networks, the damping factor ($\alpha$) adequately models friction; however, in densely connected, highly centralized datasets, propagation can oversaturate, artificially inflating risk across unaffected nodes.

## 7. Future Work
Future iterations will explore Graph Neural Networks (GNNs) for learned, dynamic propagation factors replacing static iterative diffusion, alongside LLM-driven autonomous recovery execution.

## 8. Conclusion
SCADE-X demonstrates that supply chain intelligence must evaluate both behavioral variance and structural fragility simultaneously to achieve true operational resilience.
