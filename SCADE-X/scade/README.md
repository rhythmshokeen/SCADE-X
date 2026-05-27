# SCADE — Supply Chain Anomaly Detection Engine

A process-mining based fraud detection system for procurement event logs. SCADE learns what your normal purchase order process looks like, then scores every case across up to five independent dimensions to flag anything suspicious — and explains exactly what pattern it matched.

---

## Table of Contents

1. [What This Does](#what-this-does)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Running the App](#running-the-app)
5. [Uploading Your Data](#uploading-your-data)
6. [Activity Setup — Why It Matters](#activity-setup--why-it-matters)
7. [The Detection Engine — The Math](#the-detection-engine--the-math)
8. [The Five Conformance Perspectives](#the-five-conformance-perspectives)
9. [Score Fusion — The Key Design Decision](#score-fusion--the-key-design-decision)
10. [Attack Pattern Mapping](#attack-pattern-mapping)
11. [Cross-Case Correlation](#cross-case-correlation)
12. [Dashboard & Investigation Queue](#dashboard--investigation-queue)
13. [Test Files](#test-files)
14. [Project Structure](#project-structure)

---

## What This Does

Most fraud detection tools treat procurement as a flat table of transactions and look for statistical outliers. SCADE treats it as a **process** — a sequence of steps that should happen in a specific order, performed by specific roles, within normal time windows, with consistent amounts.

The system uses **process mining** (via PM4Py) to:

1. **Learn** your normal procurement process from historical data — it discovers a Petri net model automatically
2. **Score** every purchase order case across up to five independent perspectives: control flow, time, resource, amount, and (optionally) security context
3. **Fuse** those scores using a minimum-score approach (the weakest dimension determines the composite score)
4. **Flag** cases below the anomaly threshold and map them to known fraud patterns

The result is an investigation queue of ranked cases with specific explanations: not just "this is suspicious" but "Payment Release happened before Goods Receipt, rushed in under 2 hours, and the approver account had a brute-force login attempt 45 minutes earlier from a foreign IP."

---

## Prerequisites

- **Python 3.11, 3.12, or 3.13** with the following packages installed
- macOS, Windows, or Linux

Install all dependencies:

```bash
pip install pm4py pandas numpy scikit-learn scipy flask
```

Or using the requirements file:

```bash
pip install -r requirements.txt
```

> **macOS:** If you have multiple Python versions installed, the app will auto-detect the right interpreter on startup. If it fails with `ModuleNotFoundError: No module named 'pm4py'`, run explicitly:
> ```bash
> /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 start.py
> ```

> **Windows:** Install Python from [python.org](https://www.python.org/downloads/) and make sure to check **"Add Python to PATH"** during setup. The app auto-detects the right interpreter using the Windows `py` launcher and common install paths. If it fails, run explicitly:
> ```cmd
> py -3 start.py
> ```
> or point directly to your Python executable:
> ```cmd
> C:\Python313\python.exe start.py
> ```

---

## Installation

```bash
git clone <repo-url>
cd supply-chain-anomaly-engine
pip install -r requirements.txt
```

No database, no Docker, no environment variables required. Everything runs locally.

---

## Running the App

**macOS / Linux:**
```bash
python3 start.py
```

**Windows:**
```cmd
py start.py
```

This does three things in sequence:

1. Clears any results from the previous session — every restart begins with a clean empty dashboard
2. Opens `http://127.0.0.1:5050` in your browser automatically
3. Starts the Flask server

The dashboard will show an empty state until you upload data. Go to **Upload Data** in the nav bar to begin.

To stop the server: `Ctrl+C`

---

## Uploading Your Data

SCADE expects a **procurement event log** — a file where each row is one step of one purchase order. Most ERP systems can export this directly.

### Minimum required columns

| Column | What it means | Example |
|---|---|---|
| `case_id` | Purchase order number — same value for all steps of one PO | `PO-2024-00123` |
| `activity` | The name of the step that happened | `Manager Approval` |
| `timestamp` | When the step happened | `2024-03-15 09:42:00` |

### Optional columns (improve detection accuracy)

| Column | What it enables |
|---|---|
| `user` | Segregation-of-duties checking — catches wrong person doing a step |
| `amount` | Invoice amount drift and duplicate payment detection |
| `supplier_id` | Cross-case supplier risk — flags suppliers appearing in multiple anomalous POs |

### Column names do not need to match

When you upload your file, SCADE auto-detects which column likely maps to each field using pattern matching on the column names. You then confirm or correct the mapping on screen before running. If your ERP exports `DocumentNo`, `EventName`, `ProcessDate`, `Employee`, `InvoiceAmt`, `VendorCode` — that is fine, you just map them in the UI.

### Date formats supported

Both `YYYY-MM-DD HH:MM` and `DD/MM/YYYY HH:MM` are handled automatically.

### How to export from your ERP

| ERP | How to export |
|---|---|
| **SAP** | Transaction `SE16` on tables `EKKO`/`CDHDR`, or workflow log via `SWI1`. Activity names will be SAP transaction codes (ME51N, ME54N, MIGO etc.) — configure these as aliases in Activity Setup |
| **Oracle Fusion** | Procurement → Manage Procurement Activities → Export to Excel |
| **Microsoft Dynamics 365** | Export `PurchTable` + workflow history from `WorkflowTrackingStatusTable` |
| **No ERP** | A spreadsheet with one row per approval or action on each PO — the three required columns are all you need |

---

## Activity Setup — Why It Matters

SCADE's detection engine is built around eight standard procurement steps:

1. Create Purchase Requisition
2. Manager Approval
3. Send RFQ to Supplier
4. Receive Supplier Quote
5. Create Purchase Order
6. Goods Receipt
7. Invoice Verification
8. Payment Release

Every ERP names these differently. SAP calls step 1 `ME51N`. Oracle calls it `Purchase Requisition Created`. A custom system might call it `PR Open`. If SCADE cannot recognise your activity names, it cannot check whether steps are in the right order or happening at the right time.

**Activity Setup** (accessible from the nav bar) lets you configure aliases for each of the eight steps. You add the names your ERP uses and SCADE maps them to the canonical step name before running any analysis.

The current default aliases cover the most common SAP, Oracle, and generic names. You only need to add aliases that are specific to your system.

### Why getting this right matters

The control-flow scorer replays each case against a Petri net learned from your data. If your ERP calls `Goods Receipt` something SCADE does not recognise, it will appear as an unknown step in the model — and the scoring will be inaccurate. Spending two minutes configuring aliases makes the difference between accurate detection and noise.

You can also download a pre-filled **Setup Guide** from the Upload page — it includes your current alias configuration and ERP-specific export instructions as a standalone HTML file you can share with your IT team.

---

## The Detection Engine — The Math

### Step 1: Process Discovery

SCADE uses the **Inductive Miner** algorithm (noise threshold 0.2) to discover a Petri net from your training data. A Petri net is a formal model of a process — it defines which sequences of steps are valid and which are not.

The training split is the **earliest 70% of your cases by timestamp** — assumed to represent normal behaviour before any fraud period. This is a deliberate chronological split, not a random one: you want the model to learn from the past and score the present.

### Step 2: Up to Five Perspective Scorers

Each case receives a score from 0 to 1 on up to five independent dimensions. **1 = perfectly normal. Lower = more suspicious.**

The first four perspectives run on every upload. The fifth (Security Context) is optional and activates only when you also provide a security event log.

---

## The Five Conformance Perspectives

### 1. Control Flow (CF Score)

**What it checks:** Did the steps happen in the right order? Were any steps skipped or added?

**How it works:** Token-based replay. The Petri net is treated like a board game — tokens represent process state. Each activity in the case fires a transition and moves tokens. If a transition fires but there is no token in the right place, that is a missing token — evidence the process deviated.

```
cf_score = trace_fitness = 1 - (missing_tokens + remaining_tokens) / (consumed + produced)
```

This is PM4Py's standard token-based replay fitness. A score of 1.0 means the case followed the model exactly. A score of 0.6 means 40% of the expected token flow was violated.

**What it catches:** Approval bypass (Manager Approval skipped), payment fraud (Goods Receipt and Invoice Verification skipped before payment), unauthorized supplier (RFQ and quotation steps skipped). Steps cannot be faked — if they were not in the log, the replay fails.

---

### 2. Time Perspective (Time Score)

**What it checks:** Did each step take a normal amount of time?

**How it works:** During training, SCADE measures the duration between consecutive steps for every activity and records the mean and standard deviation. At scoring time, each step duration is converted to a Z-score:

```
z = |duration - mean| / std
```

If the Z-score is below the threshold (default 2.0), no penalty is applied. Above the threshold, the excess is converted to a penalty via a sigmoid:

```
excess  = max(0, z - 2.0)
penalty = 1 - 1 / (1 + excess)
```

The sigmoid gives a smooth transition — a step at 2.1 standard deviations gets a small penalty; one at 10 standard deviations approaches a penalty of 1.0. The case time score is:

```
time_score = 1 - mean(penalties across all steps in the case)
```

**What it catches:** Fraud often involves rushing. A payment released 90 minutes after a purchase order was created is a red flag — the normal process takes days. The time scorer catches this even when all the steps are technically present and in order.

---

### 3. Resource Perspective (Resource Score)

**What it checks:** Did the right person do each step? Did the same person perform two steps that must be kept separate?

**How it works:** Two independent checks:

**Wrong-role check:** During training, SCADE learns which users (or roles) perform each activity. At scoring time, if an activity is performed by someone who never performs it in the training data, that is a wrong-role event.

**Segregation of Duties (SOD) check:** Two activity pairs are explicitly prohibited from being performed by the same user in the same case:
- `Create Purchase Requisition` + `Manager Approval` — a requester cannot approve their own purchase request
- `Create Purchase Requisition` + `Create Purchase Order` — a requester cannot create the PO for their own request

```
total_violations = wrong_role_count + sod_violation_count
resource_score   = max(0, 1 - total_violations / (checkable_steps + sod_pairs))
```

**What it catches:** SOD violations are a core procurement fraud vector. A single employee who can both raise a purchase request and approve it can authorise fraudulent purchases unchecked. This is precisely the approval_bypass attack pattern.

---

### 4. Amount Delta (Amount Score)

**What it checks:** Does the payment amount match the purchase order? Was payment released more than once?

**How it works:** Two checks per case:

**Amount drift:** Compares the `Create Purchase Order` amount to the final `Payment Release` amount.

```
drift_pct = |payment_amount - po_amount| / po_amount
```

A tolerance of 15% is allowed for legitimate rounding and fees. Beyond that:

```
excess  = drift_pct - 0.15
penalty = min(excess / 0.5, 1.0)    # caps at 1.0 when drift reaches 65%
```

**Duplicate payment:** If `Payment Release` appears more than once in a case, a hard penalty of 1.0 is applied regardless of amount.

```
amount_score = max(0, 1 - mean(penalties))
```

**What it catches:** Invoice fraud often involves a legitimate PO for a small amount followed by a payment for a much larger one. Duplicate payments are a common accounts payable fraud — the same invoice submitted and paid twice. Both are invisible to control-flow analysis since all the right steps are present, but obvious here.

---

### 5. Security Context (Security Score) — Optional

**What it checks:** Were the accounts performing critical procurement steps behaving suspiciously in the hours before they acted? Did a login brute-force precede an approval? Was there a foreign-IP login before a payment was released?

**How it works:** When you upload a security event log (SIEM/IAM export), the scorer links security events to procurement cases by matching the `user` field in the security log against the `org:resource` field in the procurement log, within a **2-hour lookback window** before each critical step.

Three steps are classified as **critical** because a compromised account at these points causes the most damage:
- `Manager Approval`
- `Create Purchase Order`
- `Payment Release`

Each suspicious event type carries a penalty:

| Event type | Penalty |
|---|---|
| brute_force | 0.85 |
| privilege_escalation | 0.75 |
| foreign_ip_login | 0.65 |
| concurrent_session | 0.45 |
| password_reset | 0.35 |
| after_hours_access | 0.30 |
| file_access_sensitive | 0.20 |
| login_failed (×n, capped at 0.50) | 0.08 each |

The worst single penalty across all critical steps determines the case score:

```
security_score = 1.0 − worst_penalty
```

A brute-force attack followed by a Manager Approval gives `1.0 − 0.85 = 0.15` — which immediately drags the composite score below the threshold regardless of how clean the procurement log looks.

**What it catches:** Credential-compromise attacks. These are invisible to the other four perspectives because the process steps are all present, in order, by the correct role — but the account doing the approving was compromised. This is the most dangerous attack class because it defeats all process-level controls.

**How to use it:** On the Upload page, after mapping your procurement columns, a second optional upload area appears for the security log. Expected columns: `timestamp`, `user`, `event_type`, `ip_address`. After uploading both files and running analysis, a Security Score column appears in the dashboard table and a Security Context panel appears on each case detail page listing each detected signal.

**If no security log is provided:** All cases receive a neutral security score of 1.0 and the pipeline behaves identically to the four-perspective baseline.

---

## Score Fusion — The Key Design Decision

Once all four scores are computed, they are combined into a single **composite score**.

### Why not a weighted average?

A weighted average is the naive approach:

```
composite = 0.40 × cf + 0.20 × time + 0.25 × resource + 0.15 × amount
```

The problem: a case with a perfect control-flow score (1.0) and a catastrophic amount score (0.0) gets a composite of roughly 0.85 — above the threshold, not flagged. The fraud is masked by unrelated good scores.

### Minimum-score fusion

SCADE uses the minimum instead:

```
composite_score = min(cf_score, time_score, resource_score, amount_score)

# With security log uploaded:
composite_score = min(cf_score, time_score, resource_score, amount_score, security_score)
```

A process is only as trustworthy as its weakest dimension. If any one perspective is compromised, the case is flagged — regardless of how well it performs on the others. This is the security analogy of a chain being only as strong as its weakest link.

The anomaly threshold is **0.875**. Cases with a composite score below this are flagged.

> The weighted average score is still computed and stored in `results.csv` as `weighted_avg_score` for comparison purposes. On the included test data, minimum-score fusion catches 100% of injected anomalies with 0 false positives. Weighted average misses roughly 75% of them because individual good scores dilute the bad ones.

---

## Attack Pattern Mapping

Flagged cases are matched to one of four known procurement fraud patterns based on which signals fired:

| Pattern | What happened | Key signals |
|---|---|---|
| **Payment Fraud** | Payment released before goods received or invoice verified | CF low (steps skipped), rushed timing, steps out of sequence |
| **Approval Bypass** | Purchase order created without manager approval | CF low, requester performed PO step (SOD violation) |
| **Duplicate Payment** | Payment Release appears twice in the same case | Amount score low, `duplicate_payment = True`, second payment inflated |
| **Unauthorized Supplier** | RFQ and quote steps skipped, supplier outside normal pool | CF low (competitive bidding bypassed), unfamiliar supplier ID |
| **Credential Compromise** | Critical step performed from a compromised or hijacked account | Security score low — brute-force, foreign-IP login, or privilege escalation detected before the step |

Each flagged case also receives:

- **Risk level:** CRITICAL / HIGH / MEDIUM based on composite score range
- **Confidence:** HIGH / MEDIUM / LOW based on how many pattern signals matched
- **Recommended action:** Specific next step — for example "Freeze payment and escalate to internal audit" or "Verify supplier registration status"

---

## Cross-Case Correlation

Individual case flagging catches fraud at the transaction level. Cross-case analysis asks whether multiple flagged cases are connected.

Three analyses run automatically after the main pipeline:

**Supplier risk:** Which suppliers appear in multiple flagged cases? A supplier appearing across 3+ anomalous POs is a stronger signal than any single case — it suggests a systemic problem with that vendor relationship rather than a one-off error.

**User risk:** Which users appear in multiple flagged cases? Identifies individuals who may be systematically circumventing controls rather than making isolated mistakes.

**Temporal clusters:** Are multiple anomalies concentrated within a 72-hour window? A burst of suspicious activity often indicates a coordinated attack or a single actor working quickly rather than isolated independent errors.

Results surface in the dashboard's Supplier Risk and User Risk panels, and are saved to `data/supplier_risk.csv` and `data/user_risk.csv`.

---

## Dashboard & Investigation Queue

The main dashboard shows:

- **KPI cards:** Total cases analysed, flagged anomaly count, average composite score, critical risk case count
- **Score distribution histogram:** Where all cases fall on the 0–1 composite scale — normal cases cluster near 1.0, anomalies cluster low. The visual separation tells you how clean your data is.
- **Attack pattern breakdown:** Donut chart of which fraud patterns were detected and in what proportion
- **Investigation queue table:** Every flagged case with all individual scores visible (including Security Score when a security log is present) so you can see exactly which dimension triggered the flag. Paginated at 25 rows per page for large datasets.
- **Supplier and user risk panels:** Cross-case entities appearing in multiple anomalous cases

### Dashboard toolbar

Above the cases table, three action buttons are always available:

| Button | What it does |
|---|---|
| **Show All Cases / Show Flagged Only** | Toggles between the full case list and flagged-only view. Normal cases appear dimmed so anomalies still stand out. |
| **↺ Re-run** | Re-runs the full pipeline on the already-uploaded file without needing to re-upload. Useful after changing activity aliases or updating the column mapping. |
| **↓ Download CSV** | Downloads `scade_results.csv` — all cases with every score, attack pattern, confidence, risk level, and signal detail. |

Clicking any case in the table opens the **Case Detail** view with:
- A radar chart comparing all perspective scores against the normal baseline (expands to a pentagon when security is active)
- Alert banner showing matched attack pattern, confidence, and recommended action
- Full signal breakdown: which steps were skipped, how many steps were rushed, SOD violations, amount drift percentage, duplicate payment flag, and security signals
- **Security Context panel** (when security log is present): lists every suspicious event detected in the lookback window — e.g. "6 failed login attempts before Manager Approval", "foreign_ip_login detected before Manager Approval (Eve)"

---

## Test Files

Three sample files are included in `data/test/` to verify the system is working correctly before connecting your real data:

### Procurement logs

| File | Cases | What to expect |
|---|---|---|
| `clean_standard.csv` | 25 normal | 0 flagged — verifies no false positives. Standard column names, auto-detected. |
| `mixed_anomalies.csv` | 20 normal + 8 anomalous | 8 flagged (2 of each attack type). Standard column names. |
| `erp_export.csv` | 15 normal + 4 anomalous | 4 flagged. ERP-style column names (`DocumentNo`, `EventName`, `EventDate`, `Employee`, `InvoiceAmt`, `VendorCode`) and DD/MM/YYYY dates — specifically designed to test the column mapping UI. |

### Security logs (paired with above)

| File | Events | What to expect |
|---|---|---|
| `clean_standard_security.csv` | 120 (all normal) | Security scores all 1.0 — no degradation. |
| `mixed_anomalies_security.csv` | 128 (28 injected) | Security scores drop on PO-0021/0022 (brute-force before Manager Approval), PO-0023/0024 (concurrent session before Create PO), PO-0025/0026 (password reset before Payment Release), PO-0027/0028 (after-hours access before Manager Approval). |
| `erp_export_security.csv` | 94 (14 injected) | Security scores drop on payment fraud and unauthorized supplier cases. |

### Recommended test sequence

1. Upload `mixed_anomalies.csv` → Run Analysis → expect 8 flagged cases, all four standard attack patterns
2. Without re-uploading, also upload `mixed_anomalies_security.csv` as the security log → Re-run → the same 8 cases now show a Security Score column, scores on credential-compromise cases drop to ~0.15, and each case detail page shows the specific events detected
3. Upload `clean_standard.csv` + `clean_standard_security.csv` → 0 flagged, all security scores 1.0 — confirms no false positives from the security layer

---

## Project Structure

```
supply-chain-anomaly-engine/
│
├── start.py                      # Single entry point — run this
├── main.py                       # Pipeline orchestration (7 steps)
├── requirements.txt
│
├── app/                          # Flask web application
│   ├── __init__.py               # App factory
│   ├── routes.py                 # All routes and API endpoints
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   ├── case_detail.html
│   │   └── activity_setup.html
│   └── static/
│       ├── css/style.css
│       └── js/
│           ├── dashboard.js
│           ├── upload.js
│           └── activity_setup.js
│
├── src/                          # Detection engine
│   ├── generate_data.py          # Synthetic procurement log generator
│   ├── generate_security_log.py  # Synthetic security log generator (paired test files)
│   ├── preprocess.py             # Log formatting and train/test split
│   ├── ingest.py                 # Real data upload, column mapping, activity normalisation
│   ├── discover.py               # Petri net process discovery (Inductive Miner)
│   ├── attack_mapper.py          # Pattern matching and risk classification (5 patterns)
│   ├── cross_case.py             # Supplier/user/temporal correlation
│   ├── evaluate.py               # Evaluation metrics and ablation study
│   └── conformance/
│       ├── control_flow.py       # Token-based replay (CF score)
│       ├── time_perspective.py   # Z-score duration analysis (time score)
│       ├── resource.py           # Role checking + SOD (resource score)
│       ├── amount_delta.py       # Drift and duplicate payment (amount score)
│       ├── security_context.py   # SIEM event correlation (security score) — Artifact 2
│       └── fusion.py             # Minimum-score composite, 4 or 5 perspectives
│
├── config/
│   ├── activity_map.json         # ERP alias configuration (editable via UI)
│   ├── activity_map_default.json # Factory defaults for reset
│   └── column_map.json           # Saved column mapping from last upload
│
├── data/
│   ├── .data_source              # Tracks current data state: real / synthetic / none
│   ├── uploads/
│   │   ├── current.csv           # Last uploaded procurement file
│   │   └── security.csv          # Last uploaded security log (optional)
│   ├── results.csv               # Pipeline output (cleared on every restart)
│   ├── supplier_risk.csv         # Cross-case supplier analysis
│   ├── user_risk.csv             # Cross-case user analysis
│   └── test/                     # Sample files for testing
│       ├── clean_standard.csv
│       ├── clean_standard_security.csv
│       ├── mixed_anomalies.csv
│       ├── mixed_anomalies_security.csv
│       ├── erp_export.csv
│       └── erp_export_security.csv
│
└── models/                       # Trained model files (auto-created on first run)
    ├── normal_model.pkl          # Petri net (net, initial marking, final marking)
    ├── time_model.pkl            # Per-activity duration statistics
    ├── resource_model.pkl        # Per-activity allowed roles/users
    └── security_model.pkl        # Security baseline (known users, normal hours)
```
