# SCADE-X Final Intelligence Fusion Engine

This document provides a mathematical and architectural specification of the SCADE-X Intelligence Fusion Engine. It represents the final decision layer where ASTRA's behavioral anomaly detection, SCADE's structural conformance, and the SCADE-X Resilience Intelligence Layer converge to produce actionable business decisions.

---

## 1. Fusion Strategy Comparison

When fusing disparate anomaly detection paradigms (latent behavioral models vs deterministic process conformance models), the naive approaches fail structurally. We evaluated four primary strategies.

### A. Weighted Average Fusion
$$S_{\text{weighted}} = 0.5 \cdot \mathcal{A}_{\text{risk}} + 0.5 \cdot (1.0 - \mathcal{S}_{\text{composite}})$$

**Failure Mode:** Masking. A sophisticated adversary executing a mathematically perfect fraud (e.g. duplicating a payment with correct roles and timing, but anomalous sequencing) will score $1.0$ on SCADE (perfect structural conformance) and $1.0$ on ASTRA (perfectly anomalous behavior). The average is $0.5$ (neutral), masking a critical threat.

### B. Minimum-Score Fusion (The SCADE Approach)
$$S_{\text{min}} = \max\big(\mathcal{A}_{\text{risk}}, \, (1.0 - \mathcal{S}_{\text{composite}})\big)$$

**Failure Mode:** False Positive Avalanche. This is the "weakest link" philosophy. Any single statistical oddity from ASTRA (e.g., a slightly unusual transformer sequence that is structurally completely benign) triggers a maximum risk flag, drowning investigators in false alerts.

### C. Learned Black-Box Fusion (e.g. Deep Neural Nets)
$$S_{\text{nn}} = f_\theta(\mathcal{A}_{\text{risk}}, \mathcal{S}_{\text{composite}}, \mathcal{R}_{\text{vuln}})$$

**Failure Mode:** Interpretability and Data Scarcity. Procurement datasets lack high-volume, reliable ground-truth labels spanning all adversarial combinations. A black box neural model cannot be audited by a forensic accountant and provides no prescriptive remedy.

### D. Hybrid Risk-Aware Fusion (Selected Strategy)
The selected approach is a **Max-Dominant Non-Linear Fusion with Resilience Amplification**. It preserves the "weakest link" sensitivity for extreme failures while using continuous behavioral probability as a scaler, bounded by systemic vulnerability.

---

## 2. Mathematical Formulation

Let $\mathcal{A}_r$ be ASTRA risk $[0, 1]$. Let $\mathcal{S}_c$ be SCADE composite $[0, 1]$ (lower is worse). Let $\mathcal{R}_v$ be Systemic Vulnerability from the Resilience layer $[0, 1]$.

First, invert SCADE into a risk metric: 
$$\mathcal{S}_r = 1.0 - \mathcal{S}_c$$

Compute Base Risk (`base_risk_score`) using a non-linear convex combination heavily biased towards the maximum threat signal, but smoothed by the average to prevent single-signal false positive spikes:
$$R_{\text{base}} = 0.7 \cdot \max(\mathcal{S}_r, \mathcal{A}_r) + 0.3 \cdot \left(\frac{\mathcal{S}_r + \mathcal{A}_r}{2}\right)$$

Apply the Resilience Amplification. If a system is inherently fragile (high vulnerability), anomalies are categorically more dangerous. We amplify the base risk by up to 20% to generate the `final_risk_score`:
$$R_{\text{final}} = \min\big(1.0, \, R_{\text{base}} \cdot (1.0 + 0.2 \cdot \mathcal{R}_v)\big)$$

---

## 3. Confidence Engine Logic

Risk severity is useless without a confidence metric. The engine computes confidence $C \in [0, 1]$ based on three dimensions:

1. **Signal Agreement ($W_1 = 0.5$)**: 
   $$A = 1.0 - |\mathcal{A}_r - \mathcal{S}_r|$$
   If ASTRA and SCADE both agree the case is anomalous (or both agree it is benign), confidence spikes. 
2. **Evidence Strength ($W_2 = 0.3$)**:
   $$E = \frac{|(\mathcal{A}_r - 0.5) \cdot 2| + |(\mathcal{S}_r - 0.5) \cdot 2|}{2}$$
   Scores at the extremes (e.g., 0.99 risk or 0.01 risk) carry higher mathematical confidence than ambiguous mid-range scores (e.g., 0.45).
3. **Subsystem Consistency ($W_3 = 0.2$)**:
   $$Con = 1.0 - \left|\frac{\mathcal{A}_r + \mathcal{S}_r}{2} - \mathcal{R}_v \right|$$
   Checks if the systemic vulnerability model agrees with the raw anomaly generators.

$$Confidence = (0.5 \cdot A) + (0.3 \cdot E) + (0.2 \cdot Con)$$

---

## 4. Threat Severity Rules

Severity is mapped not just from the final anomaly risk, but from the underlying resilience of the process.

Let $T_{\text{effective}} = (0.7 \cdot R_{\text{final}}) + (0.3 \cdot \mathcal{R}_v)$.
- **CRITICAL**: $T_{\text{effective}} > 0.85$
- **HIGH**: $T_{\text{effective}} > 0.65$
- **MEDIUM**: $T_{\text{effective}} > 0.40$
- **LOW**: Otherwise

---

## 5. Prescriptive Action Logic

The `decision_engine.py` generates specific remediation actions rather than generic alerts. It maps the worst underlying sub-dimension (from the normalized schema) to an action:

- $\mathcal{S}_{\text{security}} \rightarrow$ `CREDENTIAL_RESET` (SIEM failure)
- $\mathcal{S}_{\text{amount}} \rightarrow$ `PAYMENT_FREEZE` (Financial drift / duplicate payment)
- $\mathcal{S}_{\text{resource}} \rightarrow$ `PROCESS_ISOLATION` (Segregation of Duties failure)
- $\mathcal{A}_{\text{graph}} \rightarrow$ `SUPPLIER_ESCALATION` (Graph centrality risk)

If the threat is HIGH/CRITICAL, the action tied to the maximum risk scalar among these four is recommended. If the threat is LOW/MEDIUM, the recommendation defaults to `MONITOR`.

---

## 6. Escalation Priority

Maps the human response requirements based on Threat Severity and Mathematical Confidence:
- **IMMEDIATE**: `CRITICAL` severity with $> 75\%$ confidence.
- **URGENT**: `CRITICAL` or `HIGH` severity with $> 50\%$ confidence.
- **STANDARD**: `MEDIUM` severity, or `HIGH` severity with low confidence ($\le 50\%$).
- **NONE**: `LOW` severity.

---

## 7. Explainability & Limitations

Every decision outputs an `explainability_signals` JSON block, ensuring full interpretability for forensic analysts.
Example:
```json
{
  "astra_signal": 0.124,
  "scade_signal": 0.88,
  "systemic_vulnerability": 0.74,
  "confidence_driver": "Divergent Signals",
  "fusion_math": "Max-Dominant Non-Linear + Resilience + Propagation Amplification"
}
```

## 8. Exported Intelligence Schema

The final exported CSV (`scadex_final_intelligence.csv`) preserves all resilience columns to empirically demonstrate how resilience overrides static anomaly detection:
- `base_risk_score`: Unamplified anomaly risk.
- `final_risk_score`: Resilience-amplified systemic risk.
- `resilience_score`, `systemic_vulnerability`, `ttr`, `tts`: Kinetic structural health metrics.
- `mitigation_strategy`, `recovery_priority`: Explicit prescriptive overrides triggered when structural failure is imminent.

**Limitations**: 
- **Non-Linear Weights**: The $0.7/0.3$ splits in the hybrid fusion are heuristically derived. In a live deployment, these should be calibrated via logistic regression against historical incident response logs.
- **Action Granularity**: The prescriptive action model selects the single worst driver. Real-world mitigation might require a composite action (e.g., Freeze Payment AND Reset Credential).
