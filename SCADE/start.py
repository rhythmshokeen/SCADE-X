"""
start.py — single entry point for the SCADE application.

Runs the pipeline (if results are stale or missing), then starts
the Flask server and opens the dashboard in the browser.
"""

import os
import sys
import threading
import time
import webbrowser

# Re-exec with the correct interpreter if pm4py isn't available here
try:
    import pm4py  # noqa: F401
except ModuleNotFoundError:
    import platform
    _is_windows = platform.system() == "Windows"
    _user = os.getenv("USERNAME") or os.getenv("USER") or ""

    _candidates = [
        # macOS
        "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
        # Windows — standard installer paths
        rf"C:\Python313\python.exe",
        rf"C:\Python312\python.exe",
        rf"C:\Python311\python.exe",
        rf"C:\Users\{_user}\AppData\Local\Programs\Python\Python313\python.exe",
        rf"C:\Users\{_user}\AppData\Local\Programs\Python\Python312\python.exe",
        rf"C:\Users\{_user}\AppData\Local\Programs\Python\Python311\python.exe",
    ]

    def _relaunch(py):
        if _is_windows:
            import subprocess
            result = subprocess.run([py] + sys.argv)
            sys.exit(result.returncode)
        else:
            os.execv(py, [py] + sys.argv)

    # Try known paths first
    for _py in _candidates:
        if os.path.exists(_py):
            _relaunch(_py)

    # Windows: try the 'py' launcher which picks the best installed version
    if _is_windows:
        import subprocess
        try:
            result = subprocess.run(["py", "-3"] + sys.argv)
            sys.exit(result.returncode)
        except FileNotFoundError:
            pass

    print("ERROR: Could not find a Python with pm4py installed.")
    print("Run:  pip install pm4py pandas flask scikit-learn scipy")
    sys.exit(1)

PYTHON       = sys.executable
PORT         = 5050
HOST         = "127.0.0.1"
URL          = f"http://{HOST}:{PORT}"
RESULTS      = "data/results.csv"
UPLOAD_PATH  = "data/uploads/current.csv"
COLUMN_MAP   = "config/column_map.json"
DATA_SOURCE  = "data/.data_source"


def _real_data_available() -> bool:
    return os.path.exists(UPLOAD_PATH) and os.path.exists(COLUMN_MAP)


def _pipeline_needed() -> bool:
    if not _real_data_available():
        return False
    if not os.path.exists(RESULTS):
        return True
    results_mtime = os.path.getmtime(RESULTS)
    watched = [UPLOAD_PATH, "src/conformance/fusion.py", "src/attack_mapper.py"]
    return any(
        os.path.exists(f) and os.path.getmtime(f) > results_mtime
        for f in watched
    )


def _reset_to_empty():
    """Ensure a clean empty state if no real data exists."""
    os.makedirs("data", exist_ok=True)
    with open(DATA_SOURCE, "w") as f:
        f.write("none")
    for stale in (RESULTS, "data/supplier_risk.csv", "data/user_risk.csv"):
        if os.path.exists(stale):
            os.remove(stale)


def run_pipeline():
    print("─" * 50)
    print("  Running pipeline...")
    print("─" * 50)
    import main as pipeline
    pipeline.run()
    print("─" * 50)


def open_browser():
    # Wait for Flask to finish binding before opening
    time.sleep(1.2)
    webbrowser.open(URL)


def start_flask():
    from app import create_app
    app = create_app()
    print(f"\n  Dashboard → {URL}")
    print("  Press Ctrl+C to stop.\n")
    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Always start clean — clear any results from the previous session
    _reset_to_empty()
    print("  Starting fresh — upload your data to begin.\n")

    # ── Open browser in background ────────────────────────────
    threading.Thread(target=open_browser, daemon=True).start()

    # ── Flask (blocking) ──────────────────────────────────────
    start_flask()
