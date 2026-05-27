# SCADE-X Future Work

The current SCADE-X architecture lays the groundwork for next-generation operational intelligence. Future iterations will focus on eliminating static heuristics and advancing graph capabilities.

## 1. Graph Neural Networks (GNNs)
Currently, ASTRA uses basic topological centrality (Degree, Betweenness) to estimate supplier fragility. Moving forward, incorporating Graph Neural Networks (GNNs) would allow the system to learn multi-hop contagion patterns, directly predicting how a bankruptcy in Supplier A mathematically disrupts Workflow B.

## 2. Temporal VAEs for Process Discovery
SCADE relies on PM4Py's Inductive Miner, which enforces rigid Petri Nets. By integrating Temporal Variational Autoencoders (VAEs), the system could learn probabilistic process models, generating a natural distribution of expected time-between-activities rather than relying on standard deviation cutoffs.

## 3. Causal Resilience Models
Replacing the heuristic risk propagation math with a formal Bayesian Causal Network. This would allow the XAI engine to answer counterfactuals: *"If we had frozen the payment at Step 3, would the systemic vulnerability have remained below 0.5?"*

## 4. LLM Forensic Agents
The current Explainability Engine uses rule-based string generation. Connecting the SCADE-X JSON outputs to a locally hosted LLM (e.g., Llama 3) would enable interactive forensic investigations, allowing security teams to "chat" directly with the anomaly data.

## 5. Streaming Architectures (Online Learning)
Migrating from the current batch-based CSV data contract to Apache Kafka streaming. This would allow ASTRA and SCADE to continuously update their models (Online Learning) while SCADE-X fuses intelligence in real-time, detecting anomalies mid-transaction rather than post-mortem.
