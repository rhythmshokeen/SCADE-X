import ast
import os
import subprocess
import sys

import pandas as pd
from flask import Blueprint, jsonify, render_template, abort, request

from src.ingest import (
    read_file, auto_detect_columns, apply_column_map,
    apply_activity_map, save_column_map, ingest, data_source,
)

bp = Blueprint("main", __name__)

RESULTS_PATH = "data/results.csv"


def _load() -> pd.DataFrame | None:
    if not os.path.exists(RESULTS_PATH):
        return None
    df = pd.read_csv(RESULTS_PATH)
    # Restore list columns that CSV stringifies
    for col in ("missing_acts", "extra_acts", "activated_acts"):
        if col in df.columns:
            df[col] = df[col].apply(
                lambda v: ast.literal_eval(v) if isinstance(v, str) else []
            )
    return df


# ── Pages ──────────────────────────────────────────────────────

UPLOAD_DIR            = "data/uploads"
UPLOAD_PATH           = os.path.join(UPLOAD_DIR, "current.csv")
SECURITY_UPLOAD_PATH  = os.path.join(UPLOAD_DIR, "security.csv")


@bp.route("/")
def dashboard():
    return render_template("dashboard.html")


@bp.route("/upload")
def upload_page():
    return render_template("upload.html")


@bp.route("/case/<case_id>")
def case_detail(case_id):
    df = _load()
    if df is None:
        abort(503, "Pipeline has not been run yet.")
    row = df[df["case_id"] == case_id]
    if row.empty:
        abort(404, f"Case {case_id} not found.")
    return render_template("case_detail.html", case_id=case_id)


# ── API ────────────────────────────────────────────────────────

@bp.route("/api/stats")
def stats():
    df = _load()
    if df is None:
        return jsonify({"status": "pipeline not yet run"})

    flagged  = df[df["flagged"] == True]
    critical = flagged[flagged["risk_level"] == "CRITICAL"]
    return jsonify({
        "total":     int(len(df)),
        "flagged":   int(len(flagged)),
        "avg_score": round(float(df["composite_score"].mean()), 3),
        "critical":  int(len(critical)),
    })


@bp.route("/api/cases")
def cases():
    df = _load()
    if df is None:
        return jsonify([])

    cols = [
        "case_id", "composite_score", "cf_score", "time_score",
        "resource_score", "amount_score", "matched_attack",
        "risk_level", "confidence", "flagged", "attack_type",
        "is_anomaly", "n_fast_steps", "wrong_role_count",
        "sod_violation_count", "duplicate_payment", "amount_drift_pct",
    ]
    if "security_score" in df.columns:
        cols.insert(cols.index("amount_score") + 1, "security_score")
    if "security_events" in df.columns:
        cols.append("security_events")
    if "security_signals" in df.columns:
        cols.append("security_signals")
    out = df[[c for c in cols if c in df.columns]].copy()
    out["flagged"]           = out["flagged"].astype(bool)
    if "duplicate_payment" in out.columns:
        out["duplicate_payment"] = out["duplicate_payment"].astype(bool)
    return jsonify(out.to_dict(orient="records"))


@bp.route("/api/case/<case_id>")
def case_api(case_id):
    df = _load()
    if df is None:
        return jsonify({"error": "pipeline not yet run"}), 503

    row = df[df["case_id"] == case_id]
    if row.empty:
        return jsonify({"error": "not found"}), 404

    r = row.iloc[0].to_dict()
    # Ensure booleans serialise correctly
    r["flagged"]           = bool(r.get("flagged", False))
    r["duplicate_payment"] = bool(r.get("duplicate_payment", False))
    return jsonify(r)


@bp.route("/api/suppliers")
def suppliers():
    # Prefer the richer cross-case output if available
    if os.path.exists("data/supplier_risk.csv"):
        sup = pd.read_csv("data/supplier_risk.csv")
        sup["attack_types"] = sup["attack_types"].apply(
            lambda v: ast.literal_eval(v) if isinstance(v, str) else v
        )
        return jsonify(sup.to_dict(orient="records"))

    df = _load()
    if df is None or "supplier_id" not in (df.columns if df is not None else []):
        return jsonify([])

    counts = (
        df[df["flagged"] == True]
        .groupby("supplier_id").size()
        .reset_index(name="flagged_cases")
        .sort_values("flagged_cases", ascending=False)
    )
    return jsonify(counts.to_dict(orient="records"))


@bp.route("/api/users")
def users():
    # Prefer the richer cross-case output if available
    if os.path.exists("data/user_risk.csv"):
        return jsonify(pd.read_csv("data/user_risk.csv").to_dict(orient="records"))

    df = _load()
    if df is None:
        return jsonify([])

    flagged  = df[df["flagged"] == True]
    user_col = next((c for c in ("org:resource", "user") if c in flagged.columns), None)
    if user_col is None:
        return jsonify([])

    counts = (
        flagged.groupby(user_col).size()
        .reset_index(name="flagged_cases")
        .rename(columns={user_col: "user"})
        .sort_values("flagged_cases", ascending=False)
    )
    return jsonify(counts.to_dict(orient="records"))


ACTIVITY_MAP_PATH  = "config/activity_map.json"
ACTIVITY_MAP_DEFAULT = "config/activity_map_default.json"


@bp.route("/activity-setup")
def activity_setup():
    return render_template("activity_setup.html")


@bp.route("/api/activity-map", methods=["GET"])
def get_activity_map():
    import json
    if not os.path.exists(ACTIVITY_MAP_PATH):
        return jsonify({})
    with open(ACTIVITY_MAP_PATH) as f:
        return jsonify(json.load(f))


@bp.route("/api/activity-map", methods=["POST"])
def save_activity_map():
    import json
    data = request.get_json(force=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400
    os.makedirs("config", exist_ok=True)
    with open(ACTIVITY_MAP_PATH, "w") as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "saved"})


@bp.route("/api/activity-map/reset", methods=["POST"])
def reset_activity_map():
    import json, shutil
    # Restore from the bundled default (kept as a separate file)
    if os.path.exists(ACTIVITY_MAP_DEFAULT):
        shutil.copy(ACTIVITY_MAP_DEFAULT, ACTIVITY_MAP_PATH)
    with open(ACTIVITY_MAP_PATH) as f:
        return jsonify(json.load(f))


@bp.route("/api/upload", methods=["POST"])
def api_upload():
    """Accept a CSV/Excel file, save it, return detected columns + suggested mapping."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        return jsonify({"error": "Only CSV and Excel files are supported"}), 400

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    f.save(UPLOAD_PATH)

    try:
        df      = read_file(UPLOAD_PATH)
        columns = list(df.columns)
        suggested = auto_detect_columns(df)
    except Exception as e:
        return jsonify({"error": f"Could not read file: {e}"}), 422

    # Show a small preview so the user can verify the right file was loaded
    preview = df.head(3).to_dict(orient="records")

    return jsonify({
        "columns":      columns,
        "suggested_map": suggested,
        "row_count":    len(df),
        "preview":      preview,
    })


@bp.route("/api/upload-security", methods=["POST"])
def api_upload_security():
    """Accept a security log CSV and save it for the next pipeline run."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        return jsonify({"error": "Only CSV and Excel files are supported"}), 400
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    f.save(SECURITY_UPLOAD_PATH)
    try:
        df = read_file(SECURITY_UPLOAD_PATH)
        return jsonify({"status": "ok", "row_count": len(df)})
    except Exception as e:
        return jsonify({"error": f"Could not read file: {e}"}), 422


@bp.route("/api/security-source")
def api_security_source():
    return jsonify({"has_security": os.path.exists(SECURITY_UPLOAD_PATH)})


@bp.route("/api/configure", methods=["POST"])
def api_configure():
    """Ingest uploaded file with column mapping, then run the full pipeline."""
    body    = request.get_json(force=True)
    mapping = body.get("mapping", {})

    if not all(f in mapping for f in ("case_id", "activity", "timestamp")):
        return jsonify({"error": "case_id, activity and timestamp mappings are required"}), 400
    if not os.path.exists(UPLOAD_PATH):
        return jsonify({"error": "No uploaded file found — please upload first"}), 400

    save_column_map(mapping)

    try:
        stats = ingest(UPLOAD_PATH, mapping)
    except Exception as e:
        return jsonify({"error": f"Ingestion failed: {e}"}), 422

    try:
        import main as pipeline
        pipeline.run(retrain=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Pipeline failed: {e}"}), 500

    return jsonify({"status": "ok", "stats": stats})


@bp.route("/api/data-source")
def api_data_source():
    return jsonify({"source": data_source()})


@bp.route("/api/download-guide")
def download_guide():
    from flask import Response
    html = _build_guide_html()
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": "attachment; filename=SCADE_Setup_Guide.html"},
    )


@bp.route("/api/rerun", methods=["POST"])
def api_rerun():
    """Re-run the pipeline on the already-uploaded file (synchronous)."""
    if not os.path.exists(UPLOAD_PATH):
        return jsonify({"error": "No uploaded file found — please upload first"}), 400
    if not os.path.exists("config/column_map.json"):
        return jsonify({"error": "No column mapping found — please upload and configure first"}), 400
    try:
        import main as pipeline
        pipeline.run(retrain=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Pipeline failed: {e}"}), 500
    return jsonify({"status": "ok"})


@bp.route("/api/download-results")
def download_results():
    """Serve results.csv as a downloadable file."""
    if not os.path.exists(RESULTS_PATH):
        return jsonify({"error": "No results available — run the pipeline first"}), 404
    from flask import send_file
    return send_file(
        os.path.abspath(RESULTS_PATH),
        mimetype="text/csv",
        as_attachment=True,
        download_name="scade_results.csv",
    )


@bp.route("/api/run", methods=["POST"])
def run_pipeline():
    """Trigger a fresh pipeline run (non-blocking — returns immediately)."""
    python = sys.executable
    subprocess.Popen([python, "main.py"], cwd=os.getcwd())
    return jsonify({"status": "pipeline started"})


def _build_guide_html() -> str:
    import json
    amap = {}
    if os.path.exists(ACTIVITY_MAP_PATH):
        with open(ACTIVITY_MAP_PATH) as f:
            amap = json.load(f)

    steps_html = ""
    for i, (step, aliases) in enumerate(amap.items(), 1):
        alias_list = "".join(f"<li>{a}</li>" for a in aliases) if aliases else "<li><em>None configured yet</em></li>"
        steps_html += f"""
        <tr>
          <td style="font-weight:600;white-space:nowrap">{i}. {step}</td>
          <td><ul style="margin:0;padding-left:18px">{alias_list}</ul></td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>SCADE Setup Guide</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          max-width: 860px; margin: 40px auto; padding: 0 24px; color: #1e293b; line-height:1.6 }}
  h1   {{ color: #4f46e5; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px }}
  h2   {{ color: #1e293b; margin-top: 40px }}
  h3   {{ color: #475569; margin-top: 24px }}
  table {{ width:100%; border-collapse:collapse; margin-top:12px }}
  th    {{ background:#f1f5f9; padding:10px 14px; text-align:left; font-size:13px; text-transform:uppercase; letter-spacing:.05em }}
  td    {{ padding:10px 14px; border-bottom:1px solid #e2e8f0; font-size:14px; vertical-align:top }}
  code  {{ background:#f1f5f9; padding:2px 6px; border-radius:4px; font-size:13px }}
  .box  {{ background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:16px 20px; margin:16px 0 }}
  .note {{ background:#eff6ff; border-left:4px solid #3b82f6; padding:12px 16px; margin:16px 0 }}
  pre   {{ background:#1e293b; color:#e2e8f0; padding:16px; border-radius:8px; overflow-x:auto; font-size:13px }}
</style>
</head>
<body>

<h1>SCADE — Setup &amp; Data Guide</h1>
<p>Supply Chain Anomaly Detection Engine — generated {pd.Timestamp.now().strftime("%d %B %Y")}</p>

<h2>What Does This System Do?</h2>
<div class="box">
<p>SCADE reads your procurement event logs and <strong>learns what a normal purchase order process looks like</strong>.
It then scores every new case against that normal model across four dimensions:</p>
<ul>
  <li><strong>Control Flow</strong> — did the steps happen in the right order?</li>
  <li><strong>Time</strong> — did each step take a normal amount of time?</li>
  <li><strong>Resource</strong> — did the right person perform each step?</li>
  <li><strong>Amount</strong> — did the invoice amount match the purchase order?</li>
</ul>
<p>Cases that score poorly on any dimension are flagged and mapped to a known fraud pattern.</p>
</div>

<h2>What Data Do You Need?</h2>
<p>You need an <strong>event log</strong> — a table where each row is one step of one purchase order.
Most ERP systems can export this directly.</p>

<h3>Required Columns</h3>
<table>
  <tr><th>Field</th><th>What it is</th><th>Example</th></tr>
  <tr><td><code>case_id</code></td><td>The purchase order number — same for all events in one PO</td><td>PO-2024-00123</td></tr>
  <tr><td><code>activity</code></td><td>The name of the step that happened</td><td>Manager Approval</td></tr>
  <tr><td><code>timestamp</code></td><td>When the step happened</td><td>2024-03-15 09:42:00</td></tr>
</table>

<h3>Optional Columns (improve detection accuracy)</h3>
<table>
  <tr><th>Field</th><th>What it is</th><th>Example</th></tr>
  <tr><td><code>user</code></td><td>Who performed the step</td><td>john.smith</td></tr>
  <tr><td><code>amount</code></td><td>The monetary value at that step</td><td>14500.00</td></tr>
  <tr><td><code>supplier_id</code></td><td>Supplier or vendor identifier</td><td>VEND-0042</td></tr>
  <tr><td><code>role</code></td><td>The job role of the person</td><td>Procurement</td></tr>
</table>

<div class="note">
<strong>Note:</strong> Column names do not need to match exactly.
When you upload your file, SCADE will suggest mappings automatically and let you confirm them.
</div>

<h3>Example Rows</h3>
<pre>case_id,activity,timestamp,user,amount
PO-001,Create Purchase Requisition,2024-01-10 08:30,alice,5000
PO-001,Manager Approval,2024-01-10 14:15,david,5000
PO-001,Send RFQ to Supplier,2024-01-11 09:00,frank,5000
PO-001,Create Purchase Order,2024-01-13 11:20,frank,5000
PO-001,Goods Receipt,2024-01-17 15:00,heidi,5000
PO-001,Invoice Verification,2024-01-18 10:30,ivan,5000
PO-001,Payment Release,2024-01-19 09:00,judy,5000</pre>

<h2>How to Export From Your ERP</h2>

<h3>SAP</h3>
<div class="box">
<p>Use transaction <code>SE16</code> on table <code>EKKO</code> (purchase orders) joined with <code>CDHDR/CDPOS</code> (change documents), or use <strong>SLG1</strong> (application log). For a ready-made extract, ask your SAP Basis team to run report <code>RSSCD100</code> or export the workflow log via <code>SWI1</code>.</p>
<p>Typical SAP activity names: <em>ME51N, ME54N, MIGO, MIRO, F110</em> — configure these as aliases in Activity Setup.</p>
</div>

<h3>Oracle / PeopleSoft</h3>
<div class="box">
<p>Export from the <strong>PO_ACTIVITY_LOG</strong> or <strong>PO_HEADER_HISTORY</strong> table.
In Oracle Fusion: Procurement → Manage Procurement Activities → Export to Excel.</p>
</div>

<h3>Microsoft Dynamics 365</h3>
<div class="box">
<p>Use Power BI connector or export the <strong>PurchTable</strong> and <strong>PurchLine</strong> history tables.
The workflow history is in <strong>WorkflowTrackingStatusTable</strong>.</p>
</div>

<h3>No ERP? Build a Simple Log</h3>
<div class="box">
<p>If your team tracks procurement in Excel or email, create a spreadsheet with one row per approval
or action taken on each purchase order. The three required columns are all you need to start.</p>
</div>

<h2>The 8 Procurement Steps &amp; Their Aliases</h2>
<p>SCADE maps your ERP's event names to these standard steps using the aliases you configure in Activity Setup.
You can add as many aliases as needed.</p>
<table>
  <tr><th>Step</th><th>Configured Aliases</th></tr>
  {steps_html}
</table>

<h2>Training Split</h2>
<div class="box">
<p>SCADE automatically uses your <strong>earliest 70% of cases</strong> as the "normal" training set to
learn what a correct process looks like. The remaining 30% are scored for anomalies.</p>
<p>For best results, your data should span at least a few months of normal operations before any
suspected fraud period.</p>
</div>

<h2>What Happens After You Upload?</h2>
<ol>
  <li><strong>Column mapping</strong> — you confirm which of your columns maps to case ID, activity, timestamp etc.</li>
  <li><strong>Activity normalisation</strong> — your ERP's event names are translated to the 8 standard steps using your aliases.</li>
  <li><strong>Process discovery</strong> — the engine learns your normal procurement process from historical cases.</li>
  <li><strong>Scoring</strong> — every case is scored across all four dimensions.</li>
  <li><strong>Anomaly flagging</strong> — cases scoring below the threshold are flagged and mapped to fraud patterns.</li>
</ol>

</body>
</html>"""
