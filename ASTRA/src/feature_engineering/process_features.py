from pathlib import Path
import pandas as pd

from src.ingestion.csv_loader import (
    load_csv_data
)


EXPECTED_WORKFLOW = [
    "CREATE_PO",
    "APPROVE_PO",
    "SHIPMENT_CREATED",
    "INVENTORY_UPDATED",
    "PAYMENT_COMPLETED"
]


def generate_process_features():

    df = load_csv_data()

    grouped = df.groupby(
        "case:concept:name"
    )

    feature_rows = []

    for case_id, group in grouped:

        activities = list(
            group["concept:name"]
        )

        start_time = group[
            "time:timestamp"
        ].min()

        end_time = group[
            "time:timestamp"
        ].max()

        duration_hours = (
            end_time - start_time
        ).total_seconds() / 3600

        missing_steps = len(
            set(EXPECTED_WORKFLOW)
            - set(activities)
        )

        feature_row = {
            "case_id": case_id,
            "activity_count":
                len(activities),

            "duration_hours":
                duration_hours,

            "cost":
                group["cost"].mean(),

            "supplier":
                group["supplier"].iloc[0],

            "missing_steps":
                missing_steps
        }

        feature_rows.append(
            feature_row
        )

    features_df = pd.DataFrame(
        feature_rows
    )

    output_path = Path(
        "data/processed/process_features.csv"
    )

    output_path.parent.mkdir(
        exist_ok=True
    )

    features_df.to_csv(
        output_path,
        index=False
    )

    return features_df


if __name__ == "__main__":

    features = (
        generate_process_features()
    )

    print(
        "\nGenerated Features:\n"
    )

    print(features)

    print(
        "\nSaved to:\n"
        "data/processed/process_features.csv"
    )