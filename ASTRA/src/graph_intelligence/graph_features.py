import pickle
import pandas as pd
import networkx as nx
from pathlib import Path

GRAPH_PATH = Path("data/processed/supply_chain_graph.gpickle")
RAW_DATA = Path("data/raw/synthetic_supply_chain.csv")

OUTPUT_PATH = Path("data/processed/graph_features.csv")


def build_graph_features():

    # Load graph
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)

    # Load raw data
    df = pd.read_csv(RAW_DATA)

    # Graph metrics
    degree_centrality = nx.degree_centrality(G)

    rows = []

    for case_id, group in df.groupby("case_id"):

        supplier = group["supplier"].iloc[0]
        users = group["user"].unique()

        supplier_score = degree_centrality.get(supplier, 0)

        user_scores = [
            degree_centrality.get(user, 0)
            for user in users
        ]

        avg_user_score = (
            sum(user_scores) / len(user_scores)
            if user_scores
            else 0
        )

        rows.append({
            "case_id": case_id,
            "supplier_centrality": round(
                supplier_score, 4
            ),
            "avg_user_centrality": round(
                avg_user_score, 4
            ),
            "num_users": len(users)
        })

    features_df = pd.DataFrame(rows)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    features_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nGraph Features:\n")
    print(features_df.head())

    print("\nSaved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    build_graph_features()