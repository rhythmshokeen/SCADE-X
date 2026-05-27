"""
Synthetic security log generator.

Produces paired security logs for the three test procurement files:
  clean_standard    → no suspicious events (baseline)
  mixed_anomalies   → security events correlated with anomalous procurement cases
  erp_export        → after-hours and foreign-IP events on anomalous cases

Security log schema:
  timestamp   — when the event occurred
  user        — the user account involved
  event_type  — one of the EVENT_PENALTIES keys
  ip_address  — source IP (private range = normal, public = suspicious)
  source      — originating system (ad_server, firewall, siem, etc.)
"""

import csv
import os
import random
from datetime import datetime, timedelta

random.seed(77)

ALL_USERS = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]

NORMAL_IPS    = ["10.0.1.{0}".format(i) for i in range(10, 50)]
FOREIGN_IPS   = ["185.220.101.45", "91.108.4.12", "45.155.205.10", "194.165.16.8"]
SOURCES       = ["ad_server", "firewall", "siem", "vpn_gateway", "endpoint"]

NORMAL_EVENT_TYPES = ["login_success", "logout", "file_access", "password_change"]
SUSPICIOUS_TYPES   = [
    "login_failed", "foreign_ip_login", "concurrent_session",
    "privilege_escalation", "after_hours_access", "password_reset",
    "brute_force",
]


def _ts(base: datetime, offset_hours: float) -> str:
    return (base + timedelta(hours=offset_hours)).strftime("%Y-%m-%d %H:%M")


def _normal_background(start: datetime, end: datetime, n: int = 80) -> list:
    """Generate n normal background events across the period."""
    rows = []
    span = (end - start).total_seconds() / 3600
    for _ in range(n):
        user   = random.choice(ALL_USERS)
        offset = random.uniform(0, span)
        etype  = random.choice(NORMAL_EVENT_TYPES)
        ip     = random.choice(NORMAL_IPS)
        rows.append([
            _ts(start, offset), user, etype, ip, random.choice(SOURCES)
        ])
    return rows


# ── File 1: clean_standard_security.csv ────────────────────────────────────
def gen_clean(path: str):
    start = datetime(2024, 1, 1)
    end   = datetime(2024, 6, 30)
    rows  = _normal_background(start, end, n=120)
    _write(path, rows)
    print(f"  clean_standard_security.csv  — {len(rows)} rows (all normal)")


# ── File 2: mixed_anomalies_security.csv ───────────────────────────────────
# Timestamps are anchored to the actual critical-step times in mixed_anomalies.csv
# so that the 2-hour lookback window in security_context.py picks them up.
def gen_mixed(path: str):
    start = datetime(2024, 2, 1)
    end   = datetime(2024, 7, 31)
    rows  = _normal_background(start, end, n=100)

    # payment_fraud — brute_force + foreign_ip before Manager Approval (Eve)
    # PO-0022 Manager Approval: 2024-03-10 04:27  |  PO-0021: 2024-05-30 07:23
    for base in [datetime(2024, 3, 10, 4, 27), datetime(2024, 5, 30, 7, 23)]:
        user = "Eve"
        for i in range(6):
            rows.append([_ts(base, -1.5 + i * 0.04), user, "login_failed",
                         random.choice(FOREIGN_IPS), "firewall"])
        rows.append([_ts(base, -1.0), user, "brute_force",
                     random.choice(FOREIGN_IPS), "siem"])
        rows.append([_ts(base, -0.5), user, "foreign_ip_login",
                     random.choice(FOREIGN_IPS), "ad_server"])

    # approval_bypass — concurrent_session + privilege_escalation before Create PO (Alice)
    # PO-0023 Create PO: 2024-04-17 01:01  |  PO-0024: 2024-05-17 06:50
    for base in [datetime(2024, 4, 17, 1, 1), datetime(2024, 5, 17, 6, 50)]:
        user = "Alice"
        rows.append([_ts(base, -0.8), user, "concurrent_session",
                     random.choice(NORMAL_IPS), "vpn_gateway"])
        rows.append([_ts(base, -0.3), user, "privilege_escalation",
                     random.choice(NORMAL_IPS), "siem"])

    # duplicate_payment — password_reset before Payment Release (Ivan)
    # PO-0025 Payment Release: 2024-04-03 07:15  |  PO-0026: 2024-06-13 06:27
    for base in [datetime(2024, 4, 3, 7, 15), datetime(2024, 6, 13, 6, 27)]:
        user = "Ivan"
        rows.append([_ts(base, -1.2), user, "password_reset",
                     random.choice(NORMAL_IPS), "ad_server"])
        rows.append([_ts(base, -0.2), user, "file_access_sensitive",
                     random.choice(NORMAL_IPS), "endpoint"])

    # unauthorized_supplier — after_hours_access before Manager Approval (Eve)
    # PO-0027 Manager Approval: 2024-04-01 04:25  |  PO-0028: 2024-04-30 02:31
    for base in [datetime(2024, 4, 1, 4, 25), datetime(2024, 4, 30, 2, 31)]:
        user = "Eve"
        rows.append([_ts(base, -1.5), user, "after_hours_access",
                     random.choice(NORMAL_IPS), "siem"])
        rows.append([_ts(base, -0.8), user, "login_success",
                     random.choice(NORMAL_IPS), "ad_server"])

    rows.sort(key=lambda r: r[0])
    _write(path, rows)
    print(f"  mixed_anomalies_security.csv — {len(rows)} rows "
          f"({len(rows)-100} injected suspicious events)")


# ── File 3: erp_export_security.csv ────────────────────────────────────────
def gen_erp(path: str):
    start = datetime(2024, 5, 1)
    end   = datetime(2024, 9, 30)
    rows  = _normal_background(start, end, n=80)

    # payment_fraud cases: foreign_ip + failed logins before Manager Approval
    for base_day in [10, 35]:
        base = datetime(2024, 5, 1) + timedelta(days=base_day)
        user = random.choice(["David", "Eve"])
        for i in range(4):
            rows.append([_ts(base, -1.8 + i * 0.1), user, "login_failed",
                         random.choice(FOREIGN_IPS), "firewall"])
        rows.append([_ts(base, -0.9), user, "foreign_ip_login",
                     random.choice(FOREIGN_IPS), "ad_server"])

    # unauthorized_supplier cases: concurrent_session + after_hours
    for base_day in [20, 50]:
        base = datetime(2024, 6, 1) + timedelta(days=base_day)
        base = base.replace(hour=23, minute=30)
        user = random.choice(["Frank", "Grace"])
        rows.append([_ts(base, 0),   user, "after_hours_access",
                     random.choice(NORMAL_IPS), "siem"])
        rows.append([_ts(base, 0.2), user, "concurrent_session",
                     random.choice(NORMAL_IPS), "vpn_gateway"])

    rows.sort(key=lambda r: r[0])
    _write(path, rows)
    print(f"  erp_export_security.csv      — {len(rows)} rows "
          f"({len(rows)-80} injected suspicious events)")


def _write(path: str, rows: list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "user", "event_type", "ip_address", "source"])
        for row in sorted(rows, key=lambda r: r[0]):
            w.writerow(row)


if __name__ == "__main__":
    base = "data/test"
    print("Generating security log test files...")
    gen_clean(f"{base}/clean_standard_security.csv")
    gen_mixed(f"{base}/mixed_anomalies_security.csv")
    gen_erp(f"{base}/erp_export_security.csv")
    print("Done.")
