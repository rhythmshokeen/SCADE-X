"""
SCADE-X Resilience Engine
=========================
Core orchestrator for the Supply Chain Resilience Intelligence Layer.

Loads canonical intelligence, constructs/loads the supply chain graph,
computes dynamic graph metrics, runs cascading risk propagation,
calculates TTR/TTS, and generates recovery recommendations.

All outputs are dynamically computed—no hardcoded constants pretending
to be intelligence.
"""
import pandas as pd
import numpy as np
import json
import math
from pathlib import Path
import logging

from src.resilience.graph_engine import SupplyChainGraph
from src.resilience.risk_propagation import compute_case_propagated_risk
from src.resilience.ttr_tts_engine import (
    estimate_ttr,
    estimate_tts,
    compute_resilience_gap,
    compute_ttr_tts_fragility,
)
from src.resilience.resilience_models import (
    compute_operational_fragility,
    map_disruption_severity,
)
from src.resilience.recovery_analysis import recommend_mitigation

logger = logging.getLogger("SCADE-X-Resilience")


def _safe(val) -> float:
    if val is None:
        return 0.0
    try:
        v = float(val)
        return v if not math.isnan(v) else 0.0
    except (TypeError, ValueError):
        return 0.0


class ResilienceEngine:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.input_path = self.base_dir / "data" / "intermediate" / "unified_case_intelligence.csv"
        self.output_path = self.base_dir / "data" / "processed" / "resilience_intelligence.csv"

    def _count_violated_perspectives(self, row: pd.Series) -> int:
        threshold = 0.875
        count = 0
        for col in ["cf_score", "time_score", "resource_score", "amount_score", "security_score"]:
            val = row.get(col)
            if val is not None and not (isinstance(val, float) and math.isnan(val)):
                if float(val) < threshold:
                    count += 1
        return count

    def compute_resilience(self) -> pd.DataFrame:
        logger.info("Loading unified case intelligence...")
        if not self.input_path.exists():
            logger.error(f"Input file not found: {self.input_path}")
            return pd.DataFrame()

        df = pd.read_csv(self.input_path)

        # -------------------------------------------------------
        # A. Build / Load Supply Chain Graph and compute metrics
        # -------------------------------------------------------
        logger.info("Initialising supply chain graph engine...")
        graph_engine = SupplyChainGraph(self.base_dir)
        G = graph_engine.load_or_build()

        supplier_metrics = graph_engine.compute_supplier_metrics()
        case_supplier_map = graph_engine.map_case_to_supplier()

        # Build a lookup: supplier_id -> {degree, betweenness, pagerank, bottleneck}
        sup_lookup = {}
        if not supplier_metrics.empty:
            for _, srow in supplier_metrics.iterrows():
                sup_lookup[srow["supplier_id"]] = {
                    "degree_centrality": srow["degree_centrality"],
                    "betweenness_centrality": srow["betweenness_centrality"],
                    "pagerank": srow["pagerank"],
                    "bottleneck_score": srow["bottleneck_score"],
                }

        # -------------------------------------------------------
        # B. Compute supplier-level anomaly risks for propagation seeds
        # -------------------------------------------------------
        # Aggregate per-supplier anomaly risk from the case-level data.
        # Use the MEAN anomaly across a supplier's cases (not max).
        # Only seed suppliers whose mean risk exceeds a threshold,
        # to prevent over-saturation in small/dense graphs.
        from collections import defaultdict
        supplier_case_risks = defaultdict(list)
        for case_id, supplier_id in case_supplier_map.items():
            match = df[df["case_id"] == case_id]
            if not match.empty:
                a_risk = _safe(match.iloc[0].get("astra_risk_score", 0.0))
                s_risk = 1.0 - _safe(match.iloc[0].get("scade_composite_score", 1.0))
                supplier_case_risks[supplier_id].append(max(a_risk, s_risk))

        supplier_risk_seeds = {}
        for sid, risks in supplier_case_risks.items():
            mean_risk = sum(risks) / len(risks)
            # Only propagate from suppliers with above-average risk
            if mean_risk > 0.3:
                supplier_risk_seeds[sid] = mean_risk

        # -------------------------------------------------------
        # C. Run cascading risk propagation through the graph
        # -------------------------------------------------------
        logger.info("Running cascading risk propagation...")
        prop_df = compute_case_propagated_risk(G, case_supplier_map, supplier_risk_seeds)
        prop_lookup = dict(zip(prop_df["case_id"], prop_df["propagated_risk"]))

        # -------------------------------------------------------
        # D. Compute per-case resilience metrics
        # -------------------------------------------------------
        logger.info("Computing per-case resilience metrics...")
        records = []
        for _, row in df.iterrows():
            case_id = row.get("case_id")
            supplier_id = case_supplier_map.get(case_id, None)
            sup_info = sup_lookup.get(supplier_id, {})

            sup_criticality = sup_info.get("degree_centrality", 0.0)
            bottleneck = sup_info.get("bottleneck_score", 0.0)
            betweenness = sup_info.get("betweenness_centrality", 0.0)
            pagerank = sup_info.get("pagerank", 0.0)

            propagated_risk = prop_lookup.get(case_id, 0.0)

            # TTR / TTS
            ttr = estimate_ttr(
                row.get("resource_score"),
                row.get("time_score"),
                row.get("amount_score"),
                row.get("iforest_score"),
            )
            tts = estimate_tts(
                sup_criticality,
                row.get("cf_score"),
                row.get("security_score"),
            )
            gap = compute_resilience_gap(ttr, tts)
            ttr_tts_frag = compute_ttr_tts_fragility(ttr, tts)

            # Operational Fragility (now includes TTR/TTS)
            fragility = compute_operational_fragility(
                _safe(row.get("astra_risk_score")),
                _safe(row.get("scade_composite_score")),
                ttr_tts_frag,
            )

            # Disruption Severity
            violations = self._count_violated_perspectives(row)
            severity = map_disruption_severity(fragility, violations, gap)

            # Supplier dependency risk: combine criticality + financial drift
            amt_risk = 1.0 - _safe(row.get("amount_score"))
            dependency_risk = min(1.0, sup_criticality * (1.0 + amt_risk))

            # Systemic vulnerability: integrates fragility, propagation, security
            sec_risk = 1.0 - _safe(row.get("security_score"))
            systemic_vuln = min(
                1.0, 0.35 * fragility + 0.35 * propagated_risk + 0.15 * sec_risk + 0.15 * ttr_tts_frag
            )

            # Resilience score: inverted systemic vulnerability
            resilience_score = max(0.0, 1.0 - systemic_vuln)

            # Recovery recommendation
            rec_input = {
                "resilience_gap": gap,
                "propagated_risk": propagated_risk,
                "bottleneck_score": bottleneck,
                "supplier_criticality": sup_criticality,
                "security_score": row.get("security_score"),
                "amount_score": row.get("amount_score"),
                "resource_score": row.get("resource_score"),
                "ttr": ttr,
                "tts": tts,
            }
            recommendation = recommend_mitigation(rec_input)

            # Explainability
            signals = {
                "supplier_id": supplier_id or "unknown",
                "supplier_degree": round(sup_criticality, 4),
                "supplier_betweenness": round(betweenness, 4),
                "supplier_pagerank": round(pagerank, 4),
                "bottleneck_score": round(bottleneck, 4),
                "ttr": round(ttr, 4),
                "tts": round(tts, 4),
                "resilience_gap": round(gap, 4),
                "propagated_risk": round(propagated_risk, 4),
                "violated_perspectives": violations,
            }

            records.append({
                "case_id": case_id,
                "resilience_score": round(resilience_score, 4),
                "operational_fragility": round(fragility, 4),
                "disruption_severity": severity.value,
                "supplier_criticality": round(sup_criticality, 6),
                "dependency_risk": round(dependency_risk, 4),
                "propagated_risk": round(propagated_risk, 4),
                "systemic_vulnerability": round(systemic_vuln, 4),
                "bottleneck_score": round(bottleneck, 4),
                "ttr": round(ttr, 4),
                "tts": round(tts, 4),
                "resilience_gap": round(gap, 4),
                "recovery_complexity": round(ttr, 4),  # TTR is the recovery complexity measure
                "business_impact": round(systemic_vuln * (1.0 + 0.5 * propagated_risk), 4),
                "propagation_risk": round(propagated_risk, 4),
                "recovery_priority": recommendation["resilience_priority"],
                "mitigation_strategy": recommendation["mitigation_strategy"],
                "recommended_action": recommendation["recommended_action"],
                "continuity_risk": recommendation["continuity_risk"],
                "mitigation_explanation": recommendation["explanation"],
                "contributing_signals": json.dumps(signals),
            })

        res_df = pd.DataFrame(records)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        res_df.to_csv(self.output_path, index=False)
        logger.info(f"Resilience intelligence saved to {self.output_path} ({len(res_df)} cases)")
        return res_df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = ResilienceEngine(Path("."))
    engine.compute_resilience()
