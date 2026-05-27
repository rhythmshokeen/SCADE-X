import json
import pandas as pd


def evaluate_scores():

    with open(
        "data/processed/"
        "transformer_scores.json",
        "r"
    ) as file:

        scores = json.load(file)

    df = pd.DataFrame(scores)

    print(
        "\nTop Suspicious Cases:\n"
    )

    suspicious = df.sort_values(
        by="behavioral_anomaly_score",
        ascending=False
    )

    print(
        suspicious.head(20)
    )

    print(
        "\nSummary Statistics:\n"
    )

    print(
        suspicious[
            "behavioral_anomaly_score"
        ].describe()
    )


if __name__ == "__main__":
    evaluate_scores()