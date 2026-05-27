from pathlib import Path
import pandas as pd

from src.utils.config_loader import (
    load_config
)


REQUIRED_COLUMNS = [
    "case_id",
    "activity",
    "timestamp",
    "user",
    "supplier",
    "cost"
]


def load_csv_data():

    config = load_config()

    file_name = config[
        "dataset"
    ]["active_file"]

    file_path = Path(
        "data/raw"
    ) / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing file: {file_path}"
        )

    df = pd.read_csv(file_path)

    missing_columns = (
        set(REQUIRED_COLUMNS)
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing columns: "
            f"{missing_columns}"
        )

    df["timestamp"] = (
        pd.to_datetime(
            df["timestamp"]
        )
    )

    df = df.sort_values(
        by=[
            "case_id",
            "timestamp"
        ]
    )

    df = df.drop_duplicates()

    df = df.rename(
        columns={
            "case_id":
                "case:concept:name",

            "activity":
                "concept:name",

            "timestamp":
                "time:timestamp"
        }
    )

    return df


if __name__ == "__main__":

    data = load_csv_data()

    print(
        "\nLoaded dataset:\n"
    )

    print(data.head())

    print(
        "\nDataset info:\n"
    )

    print(data.info())