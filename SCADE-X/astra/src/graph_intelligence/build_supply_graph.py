import pandas as pd
import networkx as nx
import pickle
from pathlib import Path

RAW_DATA = Path("data/raw/synthetic_supply_chain.csv")
OUTPUT_GRAPH = Path("data/processed/supply_chain_graph.gpickle")


def build_supply_graph():

    df = pd.read_csv(RAW_DATA)

    G = nx.DiGraph()

    for case_id, group in df.groupby("case_id"):

        supplier = group["supplier"].iloc[0]

        previous_activity = None

        for _, row in group.iterrows():

            activity = row["activity"]
            user = row["user"]

            # Supplier → Activity
            G.add_edge(supplier, activity)

            # User → Activity
            G.add_edge(user, activity)

            # Activity → Activity
            if previous_activity:
                G.add_edge(previous_activity, activity)

            previous_activity = activity

    # Save graph
    with open(OUTPUT_GRAPH, "wb") as f:
        pickle.dump(G, f)

    print("\nSupply Chain Graph Built.")
    print(f"\nNodes: {G.number_of_nodes()}")
    print(f"Edges: {G.number_of_edges()}")

    print("\nSample edges:")

    for edge in list(G.edges())[:20]:
        print(edge)


if __name__ == "__main__":
    build_supply_graph()