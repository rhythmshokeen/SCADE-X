import pickle
import numpy as np
import pandas as pd

TIME_MODEL_PATH = "models/time_model.pkl"

# How many standard deviations from mean before we start penalising.
# Below this the step is considered normal.
Z_THRESHOLD = 2.0


def fit(train_df: pd.DataFrame) -> dict:
    """
    Learn per-activity duration statistics from the training log.
    train_df must have columns: case:concept:name, concept:name, time:timestamp

    Returns a dict: { activity_name: {"mean": float, "std": float} }
    """
    df = train_df.sort_values(["case:concept:name", "time:timestamp"]).copy()
    df["duration_hours"] = (
        df.groupby("case:concept:name")["time:timestamp"]
        .diff()
        .dt.total_seconds()
        .div(3600)
    )
    # Drop the first event of each case (no prior event to diff against)
    df = df.dropna(subset=["duration_hours"])

    model = {}
    for activity, group in df.groupby("concept:name"):
        durations = group["duration_hours"].values
        model[activity] = {
            "mean": float(np.mean(durations)),
            "std":  float(np.std(durations)) if len(durations) > 1 else 1.0,
        }
    return model


def save_time_model(model: dict, path=TIME_MODEL_PATH):
    with open(path, "wb") as f:
        pickle.dump(model, f)


def load_time_model(path=TIME_MODEL_PATH) -> dict:
    with open(path, "rb") as f:
        return pickle.load(f)


def _z_to_penalty(z: float) -> float:
    """
    Convert a Z-score to a 0–1 penalty.
    z <= Z_THRESHOLD → 0 penalty (normal)
    z grows beyond threshold → penalty rises toward 1
    Uses a sigmoid so the transition is smooth rather than a hard cliff.
    """
    excess = max(0.0, z - Z_THRESHOLD)
    return round(1 - 1 / (1 + excess), 4)


def score(full_df: pd.DataFrame, time_model: dict) -> pd.DataFrame:
    """
    Score every case in full_df using the fitted time model.

    Returns one row per case:
      case_id       — case identifier
      time_score    — 0–1, where 1 = no timing anomalies, 0 = severe timing violations
      n_fast_steps  — how many steps were suspiciously fast
    """
    df = full_df.sort_values(["case:concept:name", "time:timestamp"]).copy()
    df["duration_hours"] = (
        df.groupby("case:concept:name")["time:timestamp"]
        .diff()
        .dt.total_seconds()
        .div(3600)
        .fillna(0)
    )

    rows = []
    for case_id, group in df.groupby("case:concept:name"):
        penalties = []
        n_fast = 0

        for _, event in group.iterrows():
            activity = event["concept:name"]
            duration = event["duration_hours"]

            if activity not in time_model or duration == 0:
                continue

            stats = time_model[activity]
            std = stats["std"] if stats["std"] > 0 else 1.0
            z = abs(duration - stats["mean"]) / std

            # Flag as fast if duration is well below the normal mean
            if duration < stats["mean"] - Z_THRESHOLD * std:
                n_fast += 1

            penalties.append(_z_to_penalty(z))

        avg_penalty = float(np.mean(penalties)) if penalties else 0.0
        time_score  = round(1.0 - avg_penalty, 4)

        rows.append({
            "case_id":     case_id,
            "time_score":  time_score,
            "n_fast_steps": n_fast,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    from src.preprocess import load_and_format, split_log
    import os

    df = load_and_format("data/supply_chain_log.csv")
    train_df, full_df = split_log(df)

    print("Fitting time model on training data...")
    time_model = fit(train_df)
    os.makedirs("models", exist_ok=True)
    save_time_model(time_model)

    for act, stats in time_model.items():
        print(f"  {act:<35} mean={stats['mean']:6.1f}h  std={stats['std']:5.1f}h")

    print("\nScoring all cases...")
    results = score(full_df, time_model)
    print(f"Cases scored: {len(results)}")
    print(f"Score < 0.8 : {(results['time_score'] < 0.8).sum()}")
    print(f"Fast steps detected in anomalous cases:")
    print(results[results["n_fast_steps"] > 0][["case_id","time_score","n_fast_steps"]].head(8).to_string(index=False))
