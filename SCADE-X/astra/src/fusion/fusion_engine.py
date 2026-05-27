import pandas as pd
from pathlib import Path
from sklearn.preprocessing import (
    MinMaxScaler
)


ISOLATION_PATH = Path(
    "data/processed/"
    "isolation_forest_results.csv"
)

TRANSFORMER_PATH = Path(
    "data/processed/"
    "transformer_scores.json"
)

GRAPH_PATH = Path(
    "data/processed/"
    "graph_features.csv"
)

OUTPUT_PATH = Path(
    "data/processed/"
    "fused_risk_scores.csv"
)


def fusion_engine():

    # -------------------------
    # Load data
    # -------------------------

    isolation_df = pd.read_csv(
        ISOLATION_PATH
    )

    transformer_df = pd.read_json(
        TRANSFORMER_PATH
    )

    graph_df = pd.read_csv(
        GRAPH_PATH
    )

    # -------------------------
    # Merge
    # -------------------------

    merged = (
        isolation_df
        .merge(
            transformer_df,
            on="case_id"
        )
        .merge(
            graph_df,
            on="case_id"
        )
    )

    scaler = MinMaxScaler()

    # -------------------------
    # Isolation Forest
    # invert score
    # -------------------------

    merged["iforest_risk"] = (
        merged[
            "anomaly_score"
        ].max()
        -
        merged[
            "anomaly_score"
        ]
    )

    merged[
        "iforest_scaled"
    ] = scaler.fit_transform(
        merged[
            ["iforest_risk"]
        ]
    )

    # -------------------------
    # Transformer
    # -------------------------

    merged[
        "behavior_scaled"
    ] = scaler.fit_transform(
        merged[
            [
                "behavioral_anomaly_score"
            ]
        ]
    )

    # -------------------------
    # Graph
    # -------------------------

    merged[
        "supplier_scaled"
    ] = scaler.fit_transform(
        merged[
            [
                "supplier_centrality"
            ]
        ]
    )

    # -------------------------
    # Better weighted fusion
    # Transformer dominates
    # -------------------------

    merged[
        "risk_score"
    ] = (
        0.75
        *
        merged[
            "behavior_scaled"
        ]
        +
        0.20
        *
        merged[
            "iforest_scaled"
        ]
        +
        0.05
        *
        merged[
            "supplier_scaled"
        ]
    )

    # -------------------------
    # Threshold
    # consistent with benchmark
    # -------------------------

    threshold = (
        merged[
            "risk_score"
        ].mean()
        +
        (
            2
            *
            merged[
                "risk_score"
            ].std()
        )
    )

    print(
        f"\nRisk Threshold: "
        f"{threshold:.4f}"
    )

    merged[
        "predicted_anomaly"
    ] = (
        merged[
            "risk_score"
        ]
        >
        threshold
    )

    merged[
        "anomaly_label"
    ] = (
        merged[
            "predicted_anomaly"
        ]
        .map({
            True:
                "Anomaly",
            False:
                "Normal"
        })
    )

    # -------------------------
    # Sort
    # -------------------------

    merged = (
        merged
        .sort_values(
            "risk_score",
            ascending=False
        )
    )

    merged.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "\nASTRA Risk Ranking:\n"
    )

    print(
        merged[
            [
                "case_id",
                "risk_score",
                "behavioral_anomaly_score",
                "anomaly_label"
            ]
        ].head(20)
    )

    print(
        "\nSaved to:\n"
    )

    print(
        OUTPUT_PATH
    )


if __name__ == "__main__":
    fusion_engine()