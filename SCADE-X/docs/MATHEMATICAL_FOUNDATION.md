# SCADE-X Mathematical Foundation

This document formalizes the equations powering the resilience, fusion, and confidence engines in SCADE-X.

Let $\mathcal{A}_r$ be ASTRA behavioral risk $\in [0, 1]$.  
Let $\mathcal{S}_c$ be SCADE conformance $\in [0, 1]$. We map conformance to structural risk: $\mathcal{S}_r = 1.0 - \mathcal{S}_c$.

---

## 1. Resilience & Vulnerability Logic

### Operational Fragility ($F_{op}$)
Operational fragility estimates immediate structural collapse by weighting deterministic failures over probabilistic latent failures.
$$F_{op} = 0.4 \mathcal{A}_r + 0.6 \mathcal{S}_r$$

### Supplier Dependency Risk ($D_{sup}$)
Combines Topological Graph Centrality ($G$) with Financial Amount Drift ($M = 1.0 - \mathcal{S}_{\text{amount}}$). Centrality amplifies financial exposure exponentially.
$$D_{sup} = \min(1.0, \, G \cdot (1.0 + M))$$

### Risk Propagation ($P_{risk}$)
Estimates cascade potential across the supply chain, driven by dependent nodes and compromised control flows ($C = 1.0 - \mathcal{S}_{\text{cf}}$).
$$P_{risk} = \min(1.0, \, 0.5 \cdot D_{sup} + 0.3 \cdot C + 0.2 \cdot \mathcal{A}_{\text{behavior}})$$

### Systemic Vulnerability ($\mathcal{R}_v$)
The overarching multiplier denoting how fragile the entire localized procurement graph is, integrated with SIEM security threats ($Sec$).
$$\mathcal{R}_v = \min(1.0, \, 0.4 \cdot F_{op} + 0.4 \cdot P_{risk} + 0.2 \cdot Sec)$$

---

## 2. Intelligence Fusion Logic

### Hybrid Risk-Aware Fusion ($R_{\text{final}}$)
Naive weighting dilutes fraud; naive minimums create false-positive avalanches. SCADE-X implements a **Max-Dominant Non-Linear Fusion with Resilience Amplification**.

First, compute the base risk using a convex combination biased heavily toward the maximum threat signal, smoothed by the average:
$$R_{\text{base}} = 0.7 \cdot \max(\mathcal{S}_r, \mathcal{A}_r) + 0.3 \cdot \left(\frac{\mathcal{S}_r + \mathcal{A}_r}{2}\right)$$

Next, amplify the anomaly based on systemic vulnerability. (An anomaly in a highly fragile system is inherently more dangerous).
$$R_{\text{final}} = \min\big(1.0, \, R_{\text{base}} \cdot (1.0 + 0.2 \cdot \mathcal{R}_v)\big)$$

---

## 3. Confidence Logic

Risk predictions require certainty bounds. Confidence ($C \in [0, 1]$) is computed across three vectors:

1. **Signal Agreement ($A$)**: Do ASTRA and SCADE align?
   $$A = 1.0 - |\mathcal{A}_r - \mathcal{S}_r|$$
2. **Evidence Strength ($E$)**: Are the signals extreme ($0.0$ or $1.0$) or ambiguous ($0.5$)?
   $$E = \frac{|2(\mathcal{A}_r - 0.5)| + |2(\mathcal{S}_r - 0.5)|}{2}$$
3. **Subsystem Consistency ($Con$)**: Does the macroscopic vulnerability map to the microscopic anomaly risk?
   $$Con = 1.0 - \left|\frac{\mathcal{A}_r + \mathcal{S}_r}{2} - \mathcal{R}_v \right|$$

$$C = (0.5 \cdot A) + (0.3 \cdot E) + (0.2 \cdot Con)$$

---

## 4. Recovery & Triage Logic

**Recovery Complexity ($C_{rec}$)** measures the auditing cost based on Temporal delays ($T$) and Segregation of Duties violations ($R$):
$$C_{rec} = \min(1.0, \, 0.4 \cdot R + 0.4 \cdot T + 0.2 \cdot \mathcal{A}_{\text{iforest}})$$

**Escalation Priority** maps Threat Severity and Confidence to an SLA tier. For example, `CRITICAL` severity with $> 75\%$ confidence triggers an `IMMEDIATE` SLA.
