import pandas as pd
from pathlib import Path


FUSED_PATH = Path(
    "data/processed/fused_risk_scores.csv"
)

RAW_DATA_PATH = Path(
    "data/raw/synthetic_supply_chain.csv"
)

OUTPUT_PATH = Path(
    "data/processed/root_cause_report.txt"
)


NORMAL_WORKFLOW = [
    "CREATE_PO",
    "APPROVE_PO",
    "SHIPMENT_CREATED",
    "INVENTORY_UPDATED",
    "PAYMENT_COMPLETED"
]


def root_cause_explainer():

    risk_df = pd.read_csv(
        FUSED_PATH
    )

    raw_df = pd.read_csv(
        RAW_DATA_PATH
    )

    report = []

    top_cases = risk_df.head(25)

    for _, row in top_cases.iterrows():

        case_id = row["case_id"]
        risk_score = row["risk_score"]

        case_df = raw_df[
            raw_df["case_id"] == case_id
        ]

        workflow = (
            case_df["activity"]
            .tolist()
        )

        cost = (
            case_df["cost"]
            .iloc[0]
        )

        explanations = []

        # --------------------------------
        # Behavioral intelligence
        # --------------------------------
        if (
            row[
                "behavioral_anomaly_score"
            ] > 0.15
        ):
            explanations.append(
                "Transformer detected abnormal workflow behavior"
            )

        # --------------------------------
        # Statistical anomaly
        # --------------------------------
        if (
            row["anomaly_label"]
            == "Anomaly"
        ):
            explanations.append(
                "Isolation Forest detected abnormal process profile"
            )

        # --------------------------------
        # Workflow violations
        # --------------------------------
        if (
            "APPROVE_PO"
            not in workflow
        ):
            explanations.append(
                "Approval step missing"
            )

        if (
            "INVENTORY_UPDATED"
            not in workflow
        ):
            explanations.append(
                "Inventory update missing"
            )

        if (
            workflow.count(
                "APPROVE_PO"
            ) > 1
        ):
            explanations.append(
                "Duplicate approval detected"
            )

        # payment before shipment
        if (
            "PAYMENT_COMPLETED"
            in workflow
            and
            "SHIPMENT_CREATED"
            in workflow
        ):

            payment_idx = workflow.index(
                "PAYMENT_COMPLETED"
            )

            shipment_idx = workflow.index(
                "SHIPMENT_CREATED"
            )

            if (
                payment_idx
                < shipment_idx
            ):
                explanations.append(
                    "Payment completed before shipment"
                )

        # reversed workflow
        if workflow == NORMAL_WORKFLOW[::-1]:
            explanations.append(
                "Workflow reversal detected"
            )

        # --------------------------------
        # Cost anomaly
        # --------------------------------
        if cost > 15000:
            explanations.append(
                "Unusually high transaction cost"
            )

        # --------------------------------
        # Risk priority
        # --------------------------------
        if risk_score > 0.75:
            priority = "HIGH"

        elif risk_score > 0.45:
            priority = "MEDIUM"

        else:
            priority = "LOW"

        case_report = f"""
Case ID: {case_id}
==================================================
Risk Score: {risk_score:.4f}

Root Cause Analysis:
"""

        for e in explanations:
            case_report += (
                f"• {e}\n"
            )

        case_report += f"""

Workflow:
{" → ".join(workflow)}

Transaction Cost:
{cost}

Recommended Attention:
{priority}

"""

        report.append(
            case_report
        )

    final_report = "\n".join(
        report
    )

    with open(
        OUTPUT_PATH,
        "w"
    ) as f:

        f.write(
            final_report
        )

    print(
        "\nRoot Cause Report Generated"
    )

    print(
        final_report[:5000]
    )

    print("\nSaved to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    root_cause_explainer()