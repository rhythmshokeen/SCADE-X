"""
Security Context Perspective Scorer

Links security log events (logins, access control, firewall alerts) to
procurement cases by matching the user who performed each critical step
against security events in a lookback window before that step.

Catches credential-based attacks invisible to the other four perspectives:
  - Compromised approver account      → procurement log looks clean
  - After-hours session hijack        → time model doesn't flag it
  - Brute-force then approve          → resource model allows the role
  - Concurrent sessions during PO     → insider or session hijack
"""

import os
import pickle
from datetime import timedelta

import numpy as np
import pandas as pd

SECURITY_MODEL_PATH = "models/security_model.pkl"

# How far back (hours) to inspect before each critical step
LOOKBACK_HOURS = 2

# Steps where a compromised account causes the most damage
CRITICAL_STEPS = {
    "Manager Approval",
    "Create Purchase Order",
    "Payment Release",
}

# Penalty per event type (0–1 scale)
EVENT_PENALTIES = {
    "brute_force":           0.85,
    "privilege_escalation":  0.75,
    "foreign_ip_login":      0.65,
    "concurrent_session":    0.45,
    "password_reset":        0.35,
    "after_hours_access":    0.30,
    "file_access_sensitive": 0.20,
    "login_failed":          0.08,   # per occurrence, capped below
}

MAX_FAILED_LOGIN_PENALTY = 0.50   # cap on accumulated login_failed penalty


def fit(security_df: pd.DataFrame) -> dict:
    """
    Learn baseline patterns from the training security log.
    Returns a lightweight model dict — mainly used to track known-normal context.
    security_df columns: timestamp, user, event_type, ip_address
    """
    if security_df is None or security_df.empty:
        return {}

    df = security_df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", dayfirst=True)

    model = {
        "normal_hours": (7, 19),
        "known_users":  set(df["user"].dropna().unique().tolist()),
        "users_with_known_foreign_ip": (
            df[df["event_type"] == "foreign_ip_login"]["user"].unique().tolist()
        ),
    }
    return model


def save_security_model(model: dict, path: str = SECURITY_MODEL_PATH):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)


def load_security_model(path: str = SECURITY_MODEL_PATH) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "rb") as f:
        return pickle.load(f)


def score(
    full_df: pd.DataFrame,
    security_df: pd.DataFrame,
    security_model: dict,
) -> pd.DataFrame:
    """
    Score every procurement case on the security-context perspective.

    For each critical step in a case, inspects the security log for the
    performing user in the LOOKBACK_HOURS window before that step.
    The worst single critical-step penalty determines the case score.

    Returns one row per case:
      case_id           — case identifier
      security_score    — 0–1  (1 = no suspicious context detected)
      security_events   — count of suspicious security events found
      security_signals  — list of human-readable signal descriptions
    """
    cases = full_df["case:concept:name"].unique()

    # No security log uploaded → neutral scores, pipeline runs as before
    if security_df is None or security_df.empty:
        return pd.DataFrame({
            "case_id":          cases,
            "security_score":   [1.0] * len(cases),
            "security_events":  [0]   * len(cases),
            "security_signals": [[]]  * len(cases),
        })

    sec = security_df.copy()
    sec["timestamp"] = pd.to_datetime(sec["timestamp"], format="mixed", dayfirst=True)
    # Index by user for fast lookup
    sec = sec.sort_values("timestamp")

    rows = []

    for case_id, group in full_df.groupby("case:concept:name"):
        group = group.sort_values("time:timestamp")
        case_penalties = []
        case_signals   = []

        for _, event in group.iterrows():
            activity = event["concept:name"]
            if activity not in CRITICAL_STEPS:
                continue

            user      = event.get("org:resource", None)
            step_time = pd.Timestamp(event["time:timestamp"])

            if not user or str(user).lower() in ("unknown", "nan", ""):
                continue

            window_start = step_time - timedelta(hours=LOOKBACK_HOURS)
            user_sec = sec[
                (sec["user"] == user) &
                (sec["timestamp"] >= window_start) &
                (sec["timestamp"] <= step_time)
            ]

            if user_sec.empty:
                continue

            step_penalties = []
            step_signals   = []

            # Failed login accumulation
            n_failed = int((user_sec["event_type"] == "login_failed").sum())
            if n_failed > 0:
                p = min(n_failed * EVENT_PENALTIES["login_failed"], MAX_FAILED_LOGIN_PENALTY)
                step_penalties.append(p)
                step_signals.append(
                    f"{n_failed} failed login attempt{'s' if n_failed>1 else ''} "
                    f"before {activity}"
                )

            # Single-occurrence events
            for etype, penalty in EVENT_PENALTIES.items():
                if etype == "login_failed":
                    continue
                if (user_sec["event_type"] == etype).any():
                    step_penalties.append(penalty)
                    label = etype.replace("_", " ")
                    step_signals.append(f"{label} detected before {activity} ({user})")

            if step_penalties:
                case_penalties.append(max(step_penalties))
                case_signals.extend(step_signals)

        if case_penalties:
            worst          = max(case_penalties)
            security_score = round(max(0.0, 1.0 - worst), 4)
        else:
            security_score = 1.0

        rows.append({
            "case_id":          case_id,
            "security_score":   security_score,
            "security_events":  len(case_signals),
            "security_signals": case_signals,
        })

    return pd.DataFrame(rows)
