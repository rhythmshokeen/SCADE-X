"""
SCADE-X Supply Chain Graph Engine
==================================
Constructs or loads the supply chain interaction graph from ASTRA artifacts
and raw data. Computes real network-science metrics dynamically.

This module replaces static graph_score columns with dynamically computed
supplier criticality, betweenness centrality, PageRank, and structural
bottleneck detection using NetworkX.
"""
import pickle
import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from typing import Dict, Tuple
import logging

logger = logging.getLogger("SCADE-X-GraphEngine")


class SupplyChainGraph:
    """Manages the supply chain interaction graph for resilience analysis."""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        # Primary source: the gpickle built by ASTRA
        self.astra_graph_path = self.base_dir / "astra" / "data" / "processed" / "supply_chain_graph.gpickle"
        # Fallback: reconstruct from raw data
        self.raw_data_path = self.base_dir / "astra" / "data" / "raw" / "synthetic_supply_chain.csv"
        self.graph: nx.DiGraph = None

    def load_or_build(self) -> nx.DiGraph:
        """Loads ASTRA's graph if it exists, otherwise builds from raw data."""
        if self.astra_graph_path.exists():
            logger.info(f"Loading ASTRA supply chain graph from {self.astra_graph_path}")
            with open(self.astra_graph_path, "rb") as f:
                self.graph = pickle.load(f)
        elif self.raw_data_path.exists():
            logger.info("ASTRA graph not found. Reconstructing from raw data.")
            self.graph = self._build_from_raw()
        else:
            logger.warning("No graph data available. Creating minimal graph from unified intelligence.")
            self.graph = nx.DiGraph()
        return self.graph

    def _build_from_raw(self) -> nx.DiGraph:
        """Reconstructs the supply chain graph exactly as ASTRA does."""
        df = pd.read_csv(self.raw_data_path)
        G = nx.DiGraph()
        for case_id, group in df.groupby("case_id"):
            supplier = group["supplier"].iloc[0]
            previous_activity = None
            for _, row in group.iterrows():
                activity = row["activity"]
                user = row["user"]
                G.add_edge(supplier, activity)
                G.add_edge(user, activity)
                if previous_activity:
                    G.add_edge(previous_activity, activity)
                previous_activity = activity
        return G

    def compute_graph_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Computes real network-science metrics on the loaded graph.
        Returns a dict keyed by metric name, each mapping node -> score.
        """
        if self.graph is None or self.graph.number_of_nodes() == 0:
            return {"degree": {}, "betweenness": {}, "pagerank": {}}

        G = self.graph
        metrics = {
            "degree": nx.degree_centrality(G),
            "betweenness": nx.betweenness_centrality(G, normalized=True),
            "pagerank": nx.pagerank(G, alpha=0.85),
        }
        logger.info(
            f"Graph metrics computed: {G.number_of_nodes()} nodes, "
            f"{G.number_of_edges()} edges"
        )
        return metrics

    def extract_supplier_nodes(self, raw_data_path: Path = None) -> set:
        """Identifies which graph nodes are suppliers (vs users/activities)."""
        path = raw_data_path or self.raw_data_path
        if not path.exists():
            return set()
        df = pd.read_csv(path)
        return set(df["supplier"].unique())

    def compute_supplier_metrics(self) -> pd.DataFrame:
        """
        Computes per-supplier graph metrics: degree centrality, betweenness
        centrality, PageRank, and a composite bottleneck score.
        Returns a DataFrame indexed by supplier_id.
        """
        metrics = self.compute_graph_metrics()
        suppliers = self.extract_supplier_nodes()

        if not suppliers or not metrics["degree"]:
            logger.warning("No supplier nodes found in graph. Returning empty metrics.")
            return pd.DataFrame(columns=[
                "supplier_id", "degree_centrality", "betweenness_centrality",
                "pagerank", "bottleneck_score"
            ])

        rows = []
        for s in suppliers:
            deg = metrics["degree"].get(s, 0.0)
            bet = metrics["betweenness"].get(s, 0.0)
            pr = metrics["pagerank"].get(s, 0.0)
            # Bottleneck: high betweenness relative to degree signals a chokepoint
            bottleneck = bet / (deg + 1e-9)
            rows.append({
                "supplier_id": s,
                "degree_centrality": round(deg, 6),
                "betweenness_centrality": round(bet, 6),
                "pagerank": round(pr, 6),
                "bottleneck_score": round(bottleneck, 6),
            })

        df = pd.DataFrame(rows)
        # Normalise bottleneck_score to [0, 1]
        if df["bottleneck_score"].max() > 0:
            df["bottleneck_score"] = df["bottleneck_score"] / df["bottleneck_score"].max()
        return df

    def map_case_to_supplier(self) -> Dict[str, str]:
        """Returns a mapping from case_id to supplier_id using raw data."""
        if not self.raw_data_path.exists():
            return {}
        df = pd.read_csv(self.raw_data_path)
        return dict(df.groupby("case_id")["supplier"].first())
