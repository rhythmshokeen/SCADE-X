# SCADE-X End-to-End Execution Pipeline

This document outlines the usage, lifecycle, and design of the unified orchestration system that bridges ASTRA, SCADE, and all SCADE-X advanced layers (Resilience, Fusion, XAI, Benchmarking) into a single execution command.

---

## 1. Quick Start

Execute the complete end-to-end intelligence pipeline:

```bash
python main.py
```

### CLI Arguments
- `--input <path>`: Override the default procurement event log path.
- `--security-log <path>`: Override the default SIEM context log path.
- `--skip-benchmark`: Skips the ablation and robustness engines (faster execution).
- `--debug`: Enables highly verbose logging output.
- `--output-dir <path>`: Override the default user-facing output directory.
- `--config <path>`: Load a custom `yaml` configuration.

---

## 2. Pipeline Execution Order

The `SCADEXUnifiedPipeline` ensures strict chronological integrity without mutating the underlying subsystems.

1. **Input Validation**: Verifies target data paths exist.
2. **ASTRA Execution**: Invokes ASTRA in a sterile subprocess.
3. **SCADE Execution**: Invokes SCADE in a sterile subprocess.
4. **Schema Normalization**: Converts disparate outputs into `unified_case_intelligence.csv`.
5. **Resilience Intelligence**: Calculates structural fragility and output to `resilience_intelligence.csv`.
6. **Intelligence Fusion**: Merges ASTRA, SCADE, and Resilience via a Hybrid Risk-Aware model to `scadex_final_intelligence.csv`.
7. **Explainability Generation**: Computes root causes and generates forensic case reports.
8. **Benchmarking**: Runs the multi-model comparison, ablation studies, and robustness metrics.
9. **Artifact Export**: Copies all final user-facing artifacts to the target `outputs/` directory structure.

---

## 3. Subsystem Orchestration & Integrity

A core constraint of the SCADE-X architecture is **Preservation of Subsystem Integrity**. 
To achieve this, the orchestrator (`astra_runner.py` and `scade_runner.py`) uses Python's `subprocess.run(cwd=...)` to invoke ASTRA and SCADE. 

This means:
- **No Import Collisions**: ASTRA and SCADE can both have files named `src/utils.py` without namespace clashes.
- **Independent Viability**: ASTRA and SCADE can still be executed entirely independently of the SCADE-X wrapper.
- **Memory Isolation**: Memory leaks in SCADE's PM4Py engine will not corrupt the ASTRA Transformer's memory space.

---

## 4. Output Structure

All outputs intended for human consumption are copied to `outputs/`:

```text
outputs/
├── reports/                 # JSON and MD forensic case files (XAI)
├── figures/                 # ROC curves and charts (Benchmarking)
├── logs/                    # Time-stamped execution logs
├── benchmark/               # Benchmark metrics summary
├── resilience/              # Fragility and propagation risk data
├── explanations/            # Tabular root-cause explanations
└── final_intelligence/      # The ultimate SCADE-X risk scores and actions
```

Intermediate files (the raw outputs of ASTRA/SCADE before normalization) remain isolated in `data/intermediate/` and `data/processed/`.

---

## 5. Runtime Management & Failure Handling

The `RuntimeManager` tracks the lifecycle of all stages.

**Fatal vs. Recoverable Failures**:
- **ASTRA / SCADE / Fusion Failure**: Marked as FATAL. The pipeline will securely dump logs, change the status state, and `sys.exit(1)`.
- **Benchmarking Failure**: Marked as RECOVERABLE. If generating a matplotlib chart fails, the pipeline logs a warning but continues to artifact export.

---

## 6. Debugging Workflow

If an anomaly occurs:
1. Run `python main.py --debug`.
2. Inspect `outputs/logs/scadex_pipeline_{timestamp}.log`. The `RuntimeManager` logs exactly which stage threw the exception.
3. If the failure occurred during ASTRA or SCADE, the subprocess `stderr` dump is included directly in the SCADE-X log.
