import pandas as pd
import pm4py


def load_and_format(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    df = df.rename(columns={
        "case_id":   "case:concept:name",
        "activity":  "concept:name",
        "timestamp": "time:timestamp",
        "user":      "org:resource",
    })

    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
    df = df.sort_values(["case:concept:name", "time:timestamp"]).reset_index(drop=True)
    return df


def split_log(df: pd.DataFrame):
    """
    Returns (train_df, full_df).
    train_df contains only cases where every event is non-anomalous,
    so the discovered model learns purely normal behaviour.
    """
    anomalous_cases = df[df["attack_type"] != "none"]["case:concept:name"].unique()
    train_df = df[~df["case:concept:name"].isin(anomalous_cases)].copy()
    return train_df, df.copy()


def to_event_log(df: pd.DataFrame):
    """Convert a formatted DataFrame to a PM4Py EventLog."""
    return pm4py.convert_to_event_log(df)


def compute_step_durations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column `duration_hours` = time elapsed since the previous event
    in the same case. Used by the time-perspective scorer to learn normal
    step durations from the training set.
    """
    df = df.sort_values(["case:concept:name", "time:timestamp"])
    df["duration_hours"] = (
        df.groupby("case:concept:name")["time:timestamp"]
        .diff()
        .dt.total_seconds()
        .div(3600)
        .fillna(0)
    )
    return df


if __name__ == "__main__":
    df = load_and_format("data/supply_chain_log.csv")
    train_df, full_df = split_log(df)
    train_df = compute_step_durations(train_df)

    print(f"Training cases : {train_df['case:concept:name'].nunique()}")
    print(f"Full log cases : {full_df['case:concept:name'].nunique()}")
    print(f"Columns        : {list(df.columns)}")

    train_log = to_event_log(train_df)
    print(f"PM4Py EventLog : {len(train_log)} traces")
