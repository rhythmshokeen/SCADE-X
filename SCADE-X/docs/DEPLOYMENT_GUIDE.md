# SCADE-X Deployment Guide

## 1. Requirements & Installation
SCADE-X requires Python 3.10+.

```bash
# Clone the repository
git clone https://github.com/organization/SCADE-X.git
cd SCADE-X

# Install dependencies (Assuming requirements.txt encompasses ASTRA/SCADE needs)
pip install -r requirements.txt
```

*Required Core Libraries*: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `pyyaml`, `pm4py`, `torch`, `networkx`.

## 2. Execution

Run the complete pipeline from Raw Logs to Final Benchmarks in one command:

```bash
python main.py
```

### CLI Overrides
You can override the YAML configuration dynamically via the CLI:
```bash
python main.py --input data/raw/latest_erp_export.csv --debug --skip-benchmark
```

## 3. Configuration (`configs/scadex_config.yaml`)
Toggle subsystems and adjust strictness thresholds.
```yaml
pipeline:
  run_astra: true
  run_scade: true
  run_benchmarks: true
thresholds:
  fusion_severity: 0.65
```

## 4. Expected Outputs
Upon successful completion, the `outputs/` directory will populate:
- `outputs/final_intelligence/scadex_final_intelligence.csv`: The primary output containing fused risk, severity, and recommended actions.
- `outputs/reports/`: Markdown and JSON reports for every flagged case. Hand these to your audit team.
- `outputs/benchmark/`: Evaluation tables and robustness metrics.
- `outputs/figures/`: ROC Curves and visual distributions.
- `outputs/logs/`: Detailed execution trace logs for debugging.

## 5. Debugging
If execution fails:
1. Run with `--debug` for verbose output.
2. Check `outputs/logs/scadex_pipeline_*.log`. The `RuntimeManager` will explicitly state which subsystem threw the exception (e.g., "ASTRA Execution Failed").
3. Verify that `data/raw/synthetic_supply_chain.csv` exists and is formatted correctly.
