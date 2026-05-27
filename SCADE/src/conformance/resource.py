import pickle
import numpy as np
import pandas as pd

RESOURCE_MODEL_PATH = "models/resource_model.pkl"

# Activities that must be performed by different users (segregation of duties).
# Each tuple = a pair of activities that should never share the same user.
# True segregation-of-duties violations: these two activities in the same
# case must NEVER be performed by the same user because one authorises the other.
# We do NOT include Invoice Verification + Payment Release because both are
# legitimately done by Finance staff in the same case.
SOD_PAIRS = [
    ("Create Purchase Requisition", "Manager Approval"),   # requester self-approving
    ("Create Purchase Requisition", "Create Purchase Order"), # requester creating their own PO
]


def fit(train_df: pd.DataFrame) -> dict:
    """
    Learn the set of legitimate roles (or users) per activity from the training log.
    Uses 'role' if present, otherwise falls back to 'org:resource'.

    Returns { activity_name: set_of_allowed_values }
    """
    role_col = "role" if "role" in train_df.columns else "org:resource"
    model = {}
    for activity, group in train_df.groupby("concept:name"):
        if role_col in group.columns:
            model[activity] = set(group[role_col].dropna().unique())
        else:
            model[activity] = set()
    return model


def save_resource_model(model: dict, path=RESOURCE_MODEL_PATH):
    with open(path, "wb") as f:
        pickle.dump(model, f)


def load_resource_model(path=RESOURCE_MODEL_PATH) -> dict:
    with open(path, "rb") as f:
        return pickle.load(f)


def score(full_df: pd.DataFrame, resource_model: dict) -> pd.DataFrame:
    """
    Score every case on the resource perspective.

    Penalises:
      1. Wrong-role violations — a role performs an activity it never does normally
      2. Segregation-of-duties violations — same user performs two activities
         that must be kept separate

    Returns one row per case:
      case_id              — case identifier
      resource_score       — 0–1 (1 = no violations)
      wrong_role_count     — number of wrong-role events
      sod_violation_count  — number of SOD pair violations
    """
    rows = []

    for case_id, group in full_df.groupby("case:concept:name"):
        wrong_role  = 0
        sod_violations = 0
        n_checkable = 0

        # Determine which column carries the role/user identity
        has_role_col = "role" in group.columns

        # Build activity → user map for this case (for SOD checking)
        act_user: dict[str, str] = {}
        for _, event in group.iterrows():
            activity  = event["concept:name"]
            role      = event.get("role", None) if has_role_col else None
            user      = event.get("org:resource", None)
            effective = role if role else user  # use role if present, else user

            if activity in resource_model:
                n_checkable += 1
                allowed = resource_model[activity]
                if allowed and effective and effective not in allowed:
                    wrong_role += 1

            if activity and user:
                act_user[activity] = str(user)

        # Check SOD pairs
        for act_a, act_b in SOD_PAIRS:
            if act_a in act_user and act_b in act_user:
                if act_user[act_a] == act_user[act_b]:
                    sod_violations += 1

        total_violations = wrong_role + sod_violations
        max_possible     = max(n_checkable + len(SOD_PAIRS), 1)
        resource_score   = round(1.0 - total_violations / max_possible, 4)
        resource_score   = max(0.0, resource_score)

        rows.append({
            "case_id":            case_id,
            "resource_score":     resource_score,
            "wrong_role_count":   wrong_role,
            "sod_violation_count": sod_violations,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    from src.preprocess import load_and_format, split_log
    import os

    df = load_and_format("data/supply_chain_log.csv")
    train_df, full_df = split_log(df)

    print("Fitting resource model on training data...")
    resource_model = fit(train_df)
    os.makedirs("models", exist_ok=True)
    save_resource_model(resource_model)

    for act, roles in resource_model.items():
        print(f"  {act:<35} allowed roles: {sorted(roles)}")

    print("\nScoring all cases...")
    results = score(full_df, resource_model)
    print(f"Cases scored         : {len(results)}")
    print(f"Score < 1.0          : {(results['resource_score'] < 1.0).sum()}")
    print(f"Wrong role events    : {results['wrong_role_count'].sum()}")
    print(f"SOD violations       : {results['sod_violation_count'].sum()}")
    print("\nSample flagged cases:")
    flagged = results[(results["wrong_role_count"] > 0) | (results["sod_violation_count"] > 0)]
    print(flagged[["case_id","resource_score","wrong_role_count","sod_violation_count"]].head(8).to_string(index=False))
