# SCADE-X TECHNICAL SPECIFICATION

This document outlines the rigorous mathematical and algorithmic formulations underpinning the SCADE-X ecosystem.

## 1. Process Mining Formulation (SCADE Subsystem)

The SCADE subsystem evaluates deterministic conformance leveraging PM4Py. Let an event log $L$ be a multiset of traces over a set of activities $\Sigma$. The Inductive Miner extracts a block-structured Petri net $N = (P, T, F, m_0, m_f)$ representing the normative process.

**Control-Flow Replay:** Token-based replay evaluates trace fitness. For a trace $\sigma$, let $p$ be the produced tokens, $c$ be the consumed tokens, $m$ be missing tokens, and $r$ be remaining tokens.
$$ Fitness_{cf}(\sigma) = \frac{1}{2}\left(1 - \frac{m}{c}\right) + \frac{1}{2}\left(1 - \frac{r}{p}\right) $$

**Temporal Baselines:** Let $\mu_{\Delta t}$ and $\sigma_{\Delta t}$ represent the Gaussian parameters of the time taken between sequential activities. Deviations beyond $2\sigma$ reduce the temporal conformance score $S_{time}$.

## 2. Supply Chain Resilience Formulation (SCR Layer)

The SCR layer moves beyond isolated anomaly scores to quantify systemic fragility via graph theory and recovery kinetics.

### 2.1 Graph Centrality & Bottlenecks

Let $G = (V, E)$ be the supply chain interaction graph.
- **Supplier Criticality:** Measured via Degree Centrality $C_D(v) = \frac{deg(v)}{|V|-1}$
- **Structural Bottlenecks:** A node serving as a bridge between communities without robust alternative paths. 
  $$ B(v) = \frac{C_B(v)}{C_D(v) + \epsilon} $$ 
  where $C_B(v)$ is normalized Betweenness Centrality.

### 2.2 Cascading Risk Propagation

Disruptions propagate through $G$ via damped iterative diffusion. Let $r(v, t)$ be the propagated risk at node $v$ and iteration $t$, seeded by the mean subsystem anomaly score of supplier cases ($S_0$).
$$ r(v, t+1) = \alpha \sum_{u \in N_{pre}(v)} \frac{r(u, t)}{deg_{out}(u)} $$
where $\alpha \in (0, 1)$ is the damping factor (default $0.3$). Total propagated risk is bounded to $[0, 1]$.

### 2.3 Time To Recover (TTR) and Time To Survive (TTS)

Recovery kinetics dictate whether a local anomaly becomes a catastrophic failure.

**Time To Recover (TTR):** Driven by the complexity of violations (e.g., SOD rework, legal audits).
$$ TTR = 0.35(1 - S_{res}) + 0.25(1 - S_{time}) + 0.25(1 - S_{amt}) + 0.15 \cdot R_{iforest} $$

**Time To Survive (TTS):** Driven by supplier criticality and process integrity. A highly critical supplier experiencing control-flow breakdown provides a minimal survival window.
$$ TTS = \max\Big(0.05, \ 1.0 - [0.40 \cdot C_D(v) + 0.35(1 - S_{cf}) + 0.25(1 - S_{sec})]\Big) $$

**Resilience Gap:**
$$ Gap = \max(0, TTR - TTS) $$
A positive gap triggers critical escalation.

### 2.4 Operational Fragility

Operational Fragility $F \in [0, 1]$ integrates behavioral risk ($R_{ASTRA}$), conformance failure ($R_{SCADE} = 1 - S_{comp}$), and TTR/TTS ratios:
$$ F = 0.30 \cdot R_{ASTRA} + 0.40 \cdot R_{SCADE} + 0.30 \cdot \left(\frac{TTR}{TTR + TTS}\right) $$

## 3. Intelligence Fusion (Hybrid Risk-Aware)

Fusion merges probabilistic behavioral risk with deterministic non-conformance, amplified by resilience parameters.

Let $R_{base}$ be a max-dominant non-linear combination:
$$ R_{base} = 0.7 \cdot \max(R_{SCADE}, R_{ASTRA}) + 0.3 \cdot \left(\frac{R_{SCADE} + R_{ASTRA}}{2}\right) $$

Final intelligence score $I$ applies vulnerability, propagation, and gap amplification:
$$ I = \min\Big(1.0, \ R_{base} \cdot (1 + 0.15 \cdot V_{sys} + 0.10 \cdot P_{risk} + 0.10 \cdot Gap)\Big) $$

## 4. Evaluation and Benchmarking

SCADE-X is evaluated using classical machine learning classification metrics (Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC). The Benchmarking Engine natively supports Ablation Studies by selectively simulating perfect conformance (or zero risk) across isolated components (e.g., masking $V_{sys}=0$ to observe the impact of omitting the SCR layer).
