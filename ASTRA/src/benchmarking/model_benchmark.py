import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

# ==================================================
# Paths
# ==================================================

RAW_PATH = Path(
    "data/raw/"
    "synthetic_supply_chain.csv"
)

FUSION_PATH = Path(
    "data/processed/"
    "fused_risk_scores.csv"
)

TRANSFORMER_PATH = Path(
    "data/processed/"
    "transformer_scores.json"
)

IFOREST_PATH = Path(
    "data/processed/"
    "isolation_forest_results.csv"
)

OUTPUT_PATH = Path(
    "data/processed/"
    "model_benchmark.csv"
)


# ==================================================
# Evaluation Function
# ==================================================

def evaluate_model(
    y_true,
    y_pred,
    scores
):

    return {
        "Accuracy":
            round(
                accuracy_score(
                    y_true,
                    y_pred
                ),
                4
            ),

        "Precision":
            round(
                precision_score(
                    y_true,
                    y_pred,
                    zero_division=0
                ),
                4
            ),

        "Recall":
            round(
                recall_score(
                    y_true,
                    y_pred,
                    zero_division=0
                ),
                4
            ),

        "F1":
            round(
                f1_score(
                    y_true,
                    y_pred,
                    zero_division=0
                ),
                4
            ),

        "ROC-AUC":
            round(
                roc_auc_score(
                    y_true,
                    scores
                ),
                4
            )
    }


# ==================================================
# Benchmarking
# ==================================================

def benchmark_models():

    # ---------------------------------------------
    # Load data
    # ---------------------------------------------

    raw_df = pd.read_csv(
        RAW_PATH
    )

    fusion_df = pd.read_csv(
        FUSION_PATH
    )

    transformer_df = pd.read_json(
        TRANSFORMER_PATH
    )

    iforest_df = pd.read_csv(
        IFOREST_PATH
    )

    # ---------------------------------------------
    # Ground Truth
    # ---------------------------------------------

    ground_truth = (
        raw_df.groupby(
            "case_id"
        )[
            "true_anomaly"
        ]
        .max()
        .astype(int)
        .reset_index()
    )

    # ==================================================
    # Isolation Forest
    # ==================================================

    iforest_eval = (
        ground_truth.merge(
            iforest_df,
            on="case_id",
            how="inner"
        )
    )

    y_true_if = (
        iforest_eval[
            "true_anomaly"
        ]
    )

    # Invert anomaly score:
    # higher score = more anomalous

    if_scores = (
        -iforest_eval[
            "anomaly_score"
        ]
    )

    if_threshold = (
        if_scores.mean()
        +
        (
            2
            *
            if_scores.std()
        )
    )

    if_pred = (
        if_scores
        >
        if_threshold
    ).astype(int)

    print(
        f"\nIsolation Forest "
        f"Threshold: "
        f"{if_threshold:.4f}"
    )

    # ==================================================
    # Transformer
    # ==================================================

    transformer_eval = (
        ground_truth.merge(
            transformer_df,
            on="case_id",
            how="inner"
        )
    )

    y_true_transformer = (
        transformer_eval[
            "true_anomaly"
        ]
    )

    transformer_scores = (
        transformer_eval[
            "behavioral_anomaly_score"
        ]
    )

    transformer_threshold = 0.20

    transformer_pred = (
    transformer_scores
    >=
    transformer_threshold
    ).astype(int)

    print(
        f"Transformer "
        f"Threshold: "
        f"{transformer_threshold:.4f}"
    )

    # ==================================================
    # ASTRA Fusion
    # ==================================================

    fusion_eval = (
        ground_truth.merge(
            fusion_df,
            on="case_id",
            how="inner"
        )
    )

    y_true_fusion = (
        fusion_eval[
            "true_anomaly"
        ]
    )

    fusion_scores = (
        fusion_eval[
            "risk_score"
        ]
    )

    fusion_threshold = 0.75

    fusion_pred = (
    fusion_scores
    >=
    fusion_threshold
    ).astype(int)   

    print(
        f"ASTRA Fusion "
        f"Threshold: "
        f"{fusion_threshold:.4f}"
    )

    # ==================================================
    # Benchmark Table
    # ==================================================

    results = pd.DataFrame([

        {
            "Model":
                "Isolation Forest",

            **evaluate_model(
                y_true_if,
                if_pred,
                if_scores
            )
        },

        {
            "Model":
                "Transformer",

            **evaluate_model(
                y_true_transformer,
                transformer_pred,
                transformer_scores
            )
        },

        {
            "Model":
                "ASTRA Fusion",

            **evaluate_model(
                y_true_fusion,
                fusion_pred,
                fusion_scores
            )
        }

    ])

    # ---------------------------------------------
    # Print Results
    # ---------------------------------------------

    print(
        "\nModel Benchmarking\n"
    )

    print(results)

    # ---------------------------------------------
    # Save
    # ---------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        exist_ok=True
    )

    results.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "\nSaved to:\n"
        f"{OUTPUT_PATH}"
    )


# ==================================================
# Main
# ==================================================

if __name__ == "__main__":

    benchmark_models()