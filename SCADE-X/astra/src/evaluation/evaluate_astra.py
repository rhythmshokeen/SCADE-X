from pathlib import Path

import pandas as pd

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


RAW_DATA = Path(
    "data/raw/synthetic_supply_chain.csv"
)

FUSED_RESULTS = Path(
    "data/processed/fused_risk_scores.csv"
)

OUTPUT_PATH = Path(
    "data/processed/astra_evaluation.txt"
)


def evaluate_astra():

    # Load data
    raw_df = pd.read_csv(RAW_DATA)
    fused_df = pd.read_csv(FUSED_RESULTS)

    # Ground truth
    truth_df = (
        raw_df.groupby("case_id")
        .first()[["true_anomaly"]]
        .reset_index()
    )

    truth_df["true_anomaly"] = (
        truth_df["true_anomaly"]
        .astype(int)
    )

    # Convert prediction label
    fused_df["predicted_anomaly"] = (
        fused_df["anomaly_label"]
        .map({
            "Normal": 0,
            "Anomaly": 1
        })
    )

    # Merge
    merged = truth_df.merge(
        fused_df,
        on="case_id"
    )

    y_true = merged["true_anomaly"]
    y_pred = merged["predicted_anomaly"]

    # Metrics
    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_true,
        merged["risk_score"]
    )

    cm = confusion_matrix(
        y_true,
        y_pred
    )

    report = classification_report(
        y_true,
        y_pred
    )

    output = []

    output.append(
        "ASTRA Evaluation Report\n"
    )

    output.append(
        "=" * 50 + "\n"
    )

    output.append(
        f"Accuracy: {accuracy:.4f}\n"
    )

    output.append(
        f"Precision: {precision:.4f}\n"
    )

    output.append(
        f"Recall: {recall:.4f}\n"
    )

    output.append(
        f"F1 Score: {f1:.4f}\n"
    )

    output.append(
        f"ROC-AUC: {roc_auc:.4f}\n"
    )

    output.append(
        "\nConfusion Matrix:\n"
    )

    output.append(str(cm))

    output.append(
        "\n\nClassification Report:\n"
    )

    output.append(report)

    report_text = "\n".join(output)

    OUTPUT_PATH.parent.mkdir(
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w"
    ) as f:
        f.write(report_text)

    print("\nASTRA Evaluation\n")
    print(report_text)

    print(
        "\nSaved to:"
    )

    print(OUTPUT_PATH)


if __name__ == "__main__":
    evaluate_astra()