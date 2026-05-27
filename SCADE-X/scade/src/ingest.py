"""
Data ingestion layer — handles real CSV/Excel uploads.

Responsibilities:
  1. Read CSV or Excel into a DataFrame
  2. Auto-detect which columns likely map to required fields
  3. Apply a user-confirmed column mapping to rename to standard schema
  4. Optionally normalise activity names via activity_map.json
  5. Split into training (normal) and full log based on a date cutoff
"""

import json
import os
import re

import pandas as pd

REQUIRED_FIELDS  = ["case_id", "activity", "timestamp"]
OPTIONAL_FIELDS  = ["user", "amount", "supplier_id"]
STANDARD_SCHEMA  = REQUIRED_FIELDS + OPTIONAL_FIELDS

ACTIVITY_MAP_PATH = "config/activity_map.json"

# Heuristic patterns for auto-detecting column purposes
_PATTERNS = {
    "case_id":     [r"case", r"order", r"po.?num", r"requisit", r"ticket", r"id$", r"number"],
    "activity":    [r"activ", r"event", r"task", r"step", r"process", r"operation"],
    "timestamp":   [r"time", r"date", r"stamp", r"when", r"created", r"start"],
    "user":        [r"user", r"resource", r"person", r"employee", r"perform", r"actor"],
    "amount":      [r"amount", r"invoice", r"value", r"cost", r"price", r"total", r"sum"],
    "supplier_id": [r"supplier", r"vendor", r"creditor", r"partner", r"code$"],
}


def read_file(path: str) -> pd.DataFrame:
    """Read CSV or Excel. Returns raw DataFrame with original column names."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path, low_memory=False)


def auto_detect_columns(df: pd.DataFrame) -> dict:
    """
    Guess which column maps to which standard field.
    Returns { standard_field: detected_column_name } for best guesses only.
    """
    cols   = list(df.columns)
    result = {}
    used   = set()

    for field, patterns in _PATTERNS.items():
        best = None
        for col in cols:
            if col in used:
                continue
            col_lower = col.lower().replace(" ", "_")
            if any(re.search(p, col_lower) for p in patterns):
                best = col
                break
        if best:
            result[field] = best
            used.add(best)

    return result


def apply_column_map(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Rename columns according to the user-confirmed mapping.
    mapping = { standard_field: original_column_name }
    Fills missing optional columns with sensible defaults.
    """
    rename = {v: k for k, v in mapping.items() if v and v in df.columns}
    df = df.rename(columns=rename).copy()

    if "user"        not in df.columns: df["user"]        = "unknown"
    if "amount"      not in df.columns: df["amount"]      = 0.0
    if "supplier_id" not in df.columns: df["supplier_id"] = "unknown"

    # Keep only standard columns plus any extras (for transparency)
    keep = [c for c in STANDARD_SCHEMA if c in df.columns]
    return df[keep].copy()


def apply_activity_map(df: pd.DataFrame,
                       activity_map_path: str = ACTIVITY_MAP_PATH) -> pd.DataFrame:
    """
    Normalise activity names using activity_map.json.
    Unrecognised activities are left as-is so discovery can still handle them.
    """
    if not os.path.exists(activity_map_path):
        return df

    with open(activity_map_path) as f:
        amap = json.load(f)

    # Build reverse lookup: alias → canonical name
    reverse = {}
    for canonical, aliases in amap.items():
        for alias in aliases:
            reverse[alias.lower().strip()] = canonical

    df = df.copy()
    df["activity"] = df["activity"].apply(
        lambda v: reverse.get(str(v).lower().strip(), v)
    )
    return df


def format_for_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename to PM4Py schema and parse timestamps.
    Call this after apply_column_map + apply_activity_map.
    """
    df = df.rename(columns={
        "case_id":   "case:concept:name",
        "activity":  "concept:name",
        "timestamp": "time:timestamp",
        "user":      "org:resource",
    })
    df["time:timestamp"] = pd.to_datetime(df["time:timestamp"], format="mixed", dayfirst=True)
    df = df.sort_values(["case:concept:name", "time:timestamp"]).reset_index(drop=True)

    # Required ground-truth columns — unknown for real data
    if "is_anomaly"  not in df.columns: df["is_anomaly"]  = False
    if "attack_type" not in df.columns: df["attack_type"] = "unknown"

    return df


def split_by_date(df: pd.DataFrame, train_pct: float = 0.70):
    """
    Split cases into training and full sets by chronological order.
    The earliest `train_pct` of cases (by first event timestamp) form
    the training set — assumed to be representative of normal behaviour.
    """
    ts_col   = "time:timestamp"
    case_col = "case:concept:name"

    case_starts = (
        df.groupby(case_col)[ts_col].min()
        .reset_index()
        .sort_values(ts_col)
    )
    n_train  = max(1, int(len(case_starts) * train_pct))
    train_ids = set(case_starts.iloc[:n_train][case_col])

    train_df = df[df[case_col].isin(train_ids)].copy()
    return train_df, df.copy()


def save_column_map(mapping: dict, path: str = "config/column_map.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(mapping, f, indent=2)


def load_column_map(path: str = "config/column_map.json") -> dict:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


# ── Data source tracking ───────────────────────────────────────

DATA_SOURCE_PATH = "data/.data_source"


def mark_synthetic():
    os.makedirs("data", exist_ok=True)
    with open(DATA_SOURCE_PATH, "w") as f:
        f.write("synthetic")


def data_source() -> str:
    """Returns 'real', 'synthetic', or 'none'."""
    if not os.path.exists(DATA_SOURCE_PATH):
        return "none"
    return open(DATA_SOURCE_PATH).read().strip()


def ingest(upload_path: str, column_mapping: dict,
           output_path: str = "data/supply_chain_log.csv") -> dict:
    """
    Full ingestion: read → map columns → normalise activities → save.
    Returns stats dict for the UI.
    """
    df = read_file(upload_path)
    df = apply_column_map(df, column_mapping)
    df = apply_activity_map(df)
    df = format_for_pipeline(df)

    os.makedirs("data", exist_ok=True)
    df.to_csv(output_path, index=False)

    with open(DATA_SOURCE_PATH, "w") as f:
        f.write("real")

    return {
        "rows":           len(df),
        "cases":          int(df["case:concept:name"].nunique()),
        "activities":     int(df["concept:name"].nunique()),
        "activity_names": sorted(df["concept:name"].unique().tolist()),
    }
