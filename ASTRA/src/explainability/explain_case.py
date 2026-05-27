from pathlib import Path
import pandas as pd


RAW_DATA = Path(
    "data/raw/synthetic_supply_chain.csv"
)

PROCESS_FEATURES = Path(
    "data/processed/process_features.csv"
)

FUSED_RESULTS = Path(
    "data/processed/fused_risk_scores.csv"
)

OUTPUT_PATH = Path(
    "data/processed/explainability_report.txt"
)


def explain_case():

    raw_df = pd.read_csv(
        RAW_DATA
    )

    process_df = pd.read_csv(
        PROCESS_FEATURES
    )

    fused_df = pd.read_csv(
        FUSED_RESULTS
    )

    merged = fused_df.merge(
        process_df,
        on="case_id",
        how="left"
    )

    explanations = []

    suspicious_cases = merged[
        merged["anomaly_label"]
        == "Anomaly"
    ].sort_values(
        "risk_score",
        ascending=False
    )

    for _, row in (
        suspicious_cases.head(50)
        .iterrows()
    ):

        case_id = row["case_id"]

        case_events = raw_df[
            raw_df["case_id"]
            == case_id
        ]["activity"].tolist()

        explanation = []

        explanation.append(
            f"Risk Score: "
            f"{row['risk_score']:.4f}"
        )

        # Transformer signal
        if (
            row.get(
                "behavioral_anomaly_score",
                0
            )
            > 0.20
        ):
            explanation.append(
                "High behavioral anomaly "
                "score detected "
                "(workflow deviation)."
            )

        # Isolation Forest
        if (
            row.get(
                "iforest_scaled",
                0
            )
            > 0.50
        ):
            explanation.append(
                "Statistical anomaly "
                "identified by "
                "Isolation Forest."
            )

        # Missing steps (safe check)
        if (
            "missing_steps"
            in merged.columns
        ):
            if (
                row["missing_steps"]
                > 0
            ):
                explanation.append(
                    f"Workflow missing "
                    f"{int(row['missing_steps'])} "
                    f"expected step(s)."
                )

        # High duration
        if (
            "duration_hours"
            in merged.columns
        ):
            if (
                row["duration_hours"]
                > merged[
                    "duration_hours"
                ].quantile(0.90)
            ):
                explanation.append(
                    "Unusually high "
                    "process duration."
                )

        # High cost
        if (
            "cost"
            in merged.columns
        ):
            if (
                row["cost"]
                > merged[
                    "cost"
                ].quantile(0.90)
            ):
                explanation.append(
                    "Unusually high "
                    "transaction cost."
                )

        # Payment before shipment
        if (
            "PAYMENT_COMPLETED"
            in case_events
            and
            "SHIPMENT_CREATED"
            in case_events
        ):

            payment_idx = (
                case_events.index(
                    "PAYMENT_COMPLETED"
                )
            )

            shipment_idx = (
                case_events.index(
                    "SHIPMENT_CREATED"
                )
            )

            if payment_idx < shipment_idx:
                explanation.append(
                    "Payment occurred "
                    "before shipment "
                    "(workflow violation)."
                )

        # Duplicate approval
        if (
            case_events.count(
                "APPROVE_PO"
            )
            > 1
        ):
            explanation.append(
                "Duplicate approval "
                "step detected."
            )

        # Workflow reversal
        if (
            len(case_events) >= 2
            and case_events[0]
            == "PAYMENT_COMPLETED"
        ):
            explanation.append(
                "Abnormal workflow "
                "ordering detected."
            )

        explanation_text = (
            "\n".join(
                [
                    f"Case ID: {case_id}",
                    "-" * 50,
                    *explanation,
                    f"Workflow: "
                    f"{' → '.join(case_events)}",
                    "\n"
                ]
            )
        )

        explanations.append(
            explanation_text
        )

    final_report = (
        "\n".join(explanations)
    )

    OUTPUT_PATH.parent.mkdir(
        exist_ok=True
    )

    with open(
        OUTPUT_PATH,
        "w"
    ) as f:
        f.write(final_report)

    print(
        "\nExplainability Report "
        "Generated\n"
    )

    print(
        final_report[:4000]
    )

    print(
        "\nSaved to:"
    )

    print(
        OUTPUT_PATH
    )


if __name__ == "__main__":
    explain_case()