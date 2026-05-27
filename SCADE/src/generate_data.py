import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

NORMAL_PROCESS = [
    "Create Purchase Requisition",
    "Manager Approval",
    "Send RFQ to Supplier",
    "Receive Supplier Quote",
    "Create Purchase Order",
    "Goods Receipt",
    "Invoice Verification",
    "Payment Release",
]

# Normal duration ranges per step (hours): (min, max)
NORMAL_STEP_DURATIONS = {
    "Create Purchase Requisition": (1, 8),
    "Manager Approval":            (4, 48),
    "Send RFQ to Supplier":        (2, 24),
    "Receive Supplier Quote":      (24, 120),
    "Create Purchase Order":       (1, 8),
    "Goods Receipt":               (24, 96),
    "Invoice Verification":        (4, 24),
    "Payment Release":             (2, 48),
}

# Which role should perform each activity
NORMAL_RESOURCE_MAP = {
    "Create Purchase Requisition": ["Requester"],
    "Manager Approval":            ["Manager"],
    "Send RFQ to Supplier":        ["Procurement"],
    "Receive Supplier Quote":      ["Procurement"],
    "Create Purchase Order":       ["Procurement"],
    "Goods Receipt":               ["Warehouse"],
    "Invoice Verification":        ["Finance"],
    "Payment Release":             ["Finance"],
}

ALL_ROLES = ["Requester", "Manager", "Procurement", "Warehouse", "Finance"]

# Named users per role
ROLE_USERS = {
    "Requester":   ["Alice", "Bob", "Carol"],
    "Manager":     ["David", "Eve"],
    "Procurement": ["Frank", "Grace"],
    "Warehouse":   ["Heidi"],
    "Finance":     ["Ivan", "Judy"],
}

ATTACK_PATTERNS = {
    "payment_fraud": {
        "sequence": [
            "Create Purchase Requisition",
            "Manager Approval",
            "Create Purchase Order",
            "Payment Release",           # skips Goods Receipt + Invoice Verification
        ],
        # Step durations compressed to look rushed
        "fast_steps": ["Create Purchase Order", "Payment Release"],
    },
    "approval_bypass": {
        "sequence": [
            "Create Purchase Requisition",
            "Create Purchase Order",     # skips Manager Approval
            "Goods Receipt",
            "Invoice Verification",
            "Payment Release",
        ],
        # Requester performs the Create PO step (wrong role)
        "wrong_resource_step": "Create Purchase Order",
    },
    "duplicate_payment": {
        "sequence": [
            "Create Purchase Requisition",
            "Manager Approval",
            "Create Purchase Order",
            "Goods Receipt",
            "Invoice Verification",
            "Payment Release",
            "Payment Release",           # duplicate
        ],
        # Second payment has inflated amount
        "inflate_step": "Payment Release",
    },
    "unauthorized_supplier": {
        "sequence": [
            "Create Purchase Requisition",
            "Manager Approval",
            "Create Purchase Order",     # skips Send RFQ + Receive Quote
            "Goods Receipt",
            "Invoice Verification",
            "Payment Release",
        ],
        # Uses a supplier outside the normal range (SUP-021+)
        "rogue_supplier": True,
    },
}


def _pick_user(role, attack_role=None):
    """Return a named user. If attack_role is set, pick from the wrong role pool."""
    r = attack_role if attack_role else role
    users = ROLE_USERS.get(r, ["Unknown"])
    return random.choice(users)


def _step_duration(activity, fast=False):
    lo, hi = NORMAL_STEP_DURATIONS.get(activity, (1, 24))
    if fast:
        # compress to 1–4 hours regardless of normal range
        return timedelta(hours=random.uniform(0.1, 2))
    return timedelta(hours=random.uniform(lo, hi))


def _base_amount():
    return round(random.uniform(5000, 80000), 2)


def generate_log(n_normal=200, n_anomalies=40, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    rows = []
    case_counter = 1
    base_time = datetime(2024, 1, 1, 9, 0, 0)

    # ── Normal cases ─────────────────────────────────────────
    for _ in range(n_normal):
        case_id = f"PO-{case_counter:04d}"
        case_counter += 1
        ts = base_time + timedelta(days=random.randint(0, 180))
        amount = _base_amount()
        supplier = f"SUP-{random.randint(1, 20):03d}"

        for activity in NORMAL_PROCESS:
            role = random.choice(NORMAL_RESOURCE_MAP[activity])
            rows.append({
                "case_id":    case_id,
                "activity":   activity,
                "timestamp":  ts,
                "role":       role,
                "user":       _pick_user(role),
                "supplier_id": supplier,
                "amount":     amount,
                "is_anomaly": False,
                "attack_type": "none",
            })
            ts += _step_duration(activity)

    # ── Anomalous cases ───────────────────────────────────────
    attack_types = list(ATTACK_PATTERNS.keys())

    for i in range(n_anomalies):
        case_id = f"PO-{case_counter:04d}"
        case_counter += 1
        attack_name = attack_types[i % len(attack_types)]
        pattern = ATTACK_PATTERNS[attack_name]
        sequence = pattern["sequence"]

        ts = base_time + timedelta(days=random.randint(0, 180))
        base_amount = _base_amount()
        supplier = (
            f"SUP-{random.randint(21, 30):03d}"
            if pattern.get("rogue_supplier")
            else f"SUP-{random.randint(1, 20):03d}"
        )

        seen_payment = False
        for activity in sequence:
            role = random.choice(NORMAL_RESOURCE_MAP.get(activity, ["Unknown"]))

            # approval_bypass: requester does the PO step (segregation of duties violation)
            actual_role = role
            if pattern.get("wrong_resource_step") == activity:
                actual_role = "Requester"

            # payment_fraud: rush the suspicious steps
            fast = activity in pattern.get("fast_steps", [])

            # duplicate_payment: inflate the second Payment Release
            if activity == "Payment Release" and pattern.get("inflate_step") == activity:
                if seen_payment:
                    amount = round(base_amount * random.uniform(1.5, 3.0), 2)
                else:
                    amount = base_amount
                    seen_payment = True
            else:
                amount = base_amount

            rows.append({
                "case_id":     case_id,
                "activity":    activity,
                "timestamp":   ts,
                "role":        actual_role,
                "user":        _pick_user(actual_role),
                "supplier_id": supplier,
                "amount":      amount,
                "is_anomaly":  True,
                "attack_type": attack_name,
            })
            ts += _step_duration(activity, fast=fast)

    df = pd.DataFrame(rows)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    df = generate_log()
    df.to_csv("data/supply_chain_log.csv", index=False)
    print(f"Generated {df['case_id'].nunique()} cases ({df['is_anomaly'].sum()} anomalous events)")
    print(df.groupby("attack_type")["case_id"].nunique().to_string())
