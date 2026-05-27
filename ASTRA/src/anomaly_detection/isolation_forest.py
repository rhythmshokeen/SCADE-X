from pathlib import Path
import pandas as pd

from sklearn.ensemble import (
    IsolationForest
)


def run_isolation_forest():

    df = pd.read_csv(
        "data/processed/process_features.csv"
    )

    model_features = [
        "activity_count",
        "duration_hours",
        "cost",
        "missing_steps"
    ]

    X = df[model_features]

    model = IsolationForest(
        contamination=0.2,
        random_state=42
    )

    model.fit(X)

    df["anomaly_score"] = (
        model.decision_function(X)
    )

    df["anomaly_label"] = (
        model.predict(X)
    )

    df["anomaly_label"] = (
        df["anomaly_label"]
        .map({
            1: "Normal",
            -1: "Anomaly"
        })
    )

    output_path = Path(
        "data/processed/"
        "isolation_forest_results.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        "\nASTRA Anomaly Results:\n"
    )

    print(
        df[
            [
                "case_id",
                "anomaly_score",
                "anomaly_label"
            ]
        ]
    )

    print(
        "\nSaved to:\n"
        "data/processed/"
        "isolation_forest_results.csv"
    )


if __name__ == "__main__":
    run_isolation_forest()