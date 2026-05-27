"""
SCADE-X Cascading Risk Propagation Engine
==========================================
Implements graph-based disruption propagation using NetworkX.

Replaces the old algebraic placeholders with actual network-science
propagation: if a supplier node becomes risky, risk flows downstream
through the graph to connected suppliers, activities, and cases.

The propagation model is a damped iterative diffusion:
    risk(v, t+1) = α · Σ_{u∈N(v)} w(u,v) · risk(u, t)
where α is the damping factor (analogous to PageRank's teleportation)
and w(u,v) is the normalised edge weight.
"""
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict
import logging

logger = logging.getLogger("SCADE-X-Propagation")

# Damping factor: controls how much risk decays at each hop.
# 0.3 means each hop transmits 30% of the upstream risk.
DAMPING_ALPHA = 0.3

# Number of propagation iterations (hops).
MAX_HOPS = 3


def propagate_risk_through_graph(
    G: nx.DiGraph,
    seed_risks: Dict[str, float],
    alpha: float = DAMPING_ALPHA,
    max_hops: int = MAX_HOPS,
) -> Dict[str, float]:
    """
    Propagates risk from seed nodes through the directed graph.

    Parameters
    ----------
    G : nx.DiGraph
        The supply chain interaction graph.
    seed_risks : dict
        Mapping from node name to an initial risk score [0, 1].
        Typically supplier nodes with anomaly scores.
    alpha : float
        Damping factor per hop (0 < α < 1).
    max_hops : int
        Maximum propagation depth.

    Returns
    -------
    dict
        Mapping from every reachable node to its accumulated
        propagated risk score, capped at 1.0.
    """
    if G.number_of_nodes() == 0:
        return {}

    # Initialise risk vector
    risk = {n: 0.0 for n in G.nodes()}
    for node, r in seed_risks.items():
        if node in risk:
            risk[node] = r

    # Iterative damped diffusion
    for hop in range(max_hops):
        new_risk = {n: 0.0 for n in G.nodes()}
        for node in G.nodes():
            if risk[node] <= 0:
                continue
            successors = list(G.successors(node))
            if not successors:
                continue
            transmitted = alpha * risk[node] / len(successors)
            for succ in successors:
                new_risk[succ] += transmitted
        # Accumulate (seed nodes keep their original risk)
        for node in G.nodes():
            risk[node] = min(1.0, risk[node] + new_risk[node])

    return risk


def compute_case_propagated_risk(
    G: nx.DiGraph,
    case_supplier_map: Dict[str, str],
    supplier_risk_scores: Dict[str, float],
) -> pd.DataFrame:
    """
    Computes propagated risk for each case via its supplier.

    1. Seeds the graph with supplier-level anomaly risk.
    2. Runs damped iterative diffusion.
    3. Maps each case to its supplier's post-propagation risk.

    Returns a DataFrame with case_id and propagated_risk.
    """
    if not supplier_risk_scores or G.number_of_nodes() == 0:
        logger.warning("No supplier risks or empty graph. Returning zero propagation.")
        cases = list(case_supplier_map.keys())
        return pd.DataFrame({
            "case_id": cases,
            "propagated_risk": [0.0] * len(cases),
        })

    # Run propagation
    all_risks = propagate_risk_through_graph(G, supplier_risk_scores)

    rows = []
    for case_id, supplier_id in case_supplier_map.items():
        prop_risk = all_risks.get(supplier_id, 0.0)
        rows.append({"case_id": case_id, "propagated_risk": round(prop_risk, 6)})

    return pd.DataFrame(rows)
