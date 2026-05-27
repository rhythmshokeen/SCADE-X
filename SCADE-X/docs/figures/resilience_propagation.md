# Cascading Risk Propagation

```mermaid
flowchart LR
    subgraph Seeds["Seed Risk Computation"]
        direction TB
        CS["Per-case ASTRA risk<br/>+ SCADE inversion"]
        AGG["Aggregate per-supplier:<br/>max(ASTRA_risk, 1 - SCADE_comp)"]
        CS --> AGG
    end

    subgraph Graph["Supply Chain DiGraph"]
        direction TB
        SUP_A["Supplier A<br/>risk=0.8"]
        SUP_B["Supplier B<br/>risk=0.2"]
        ACT1["Activity: Create PO"]
        ACT2["Activity: Approve PO"]
        ACT3["Activity: Ship Goods"]
        USR1["User: john_doe"]

        SUP_A -->|edge| ACT1
        USR1 -->|edge| ACT1
        ACT1 -->|edge| ACT2
        ACT2 -->|edge| ACT3
        SUP_B -->|edge| ACT3
    end

    subgraph Diffusion["Damped Iterative Diffusion"]
        direction TB
        INIT["Initialize: risk_v = seed or 0"]
        HOP1["Hop 1: new_risk_v += α · risk_u / |successors_u|"]
        HOP2["Hop 2: Accumulate, cap at 1.0"]
        HOP3["Hop 3: Final propagated risk"]
        INIT --> HOP1
        HOP1 --> HOP2
        HOP2 --> HOP3
    end

    subgraph Params["Parameters"]
        ALPHA["α = 0.5 (damping)"]
        HOPS["max_hops = 3"]
    end

    subgraph Output["Output"]
        MAP["case_id → propagated_risk<br/>(via supplier lookup)"]
    end

    Seeds --> Graph
    Graph --> Diffusion
    Params --> Diffusion
    Diffusion --> Output

    style Seeds fill:#fff3e0
    style Graph fill:#e8f4fd
    style Diffusion fill:#fce4ec
    style Params fill:#f5f5f5
    style Output fill:#e8f5e9
```

## Mathematical Formulation

The propagation follows damped iterative diffusion over a directed graph $G = (V, E)$:

**Per-hop update:**

$$\text{new\_risk}(v) = \sum_{u \in \text{predecessors}(v)} \frac{\alpha \cdot \text{risk}(u)}{|\text{successors}(u)|}$$

**Accumulation with cap:**

$$\text{risk}(v) \leftarrow \min\left(1.0, \; \text{risk}(v) + \text{new\_risk}(v)\right)$$

where $\alpha = 0.5$ and the process runs for $k = 3$ hops.
