# SCADE-X — Project Structure

> Generated during Phase 1 (Scaffold) — 2026-05-25

---

## 1. Overview

SCADE-X is the unified integration layer that orchestrates the **ASTRA** and **SCADE** subsystems into a single, cohesive ISR (Intelligence, Surveillance, and Reconnaissance) pipeline. This document describes the project layout, the purpose of every directory, and the subsystem integrity guarantees.

---

## 2. Directory Tree

```
SCADE-X/
│
├── docs/                          # Project documentation
│   └── PROJECT_STRUCTURE.md       # ← this file
│
├── src/                           # SCADE-X integration source code
│   ├── orchestration/             # Cross-system pipeline orchestration
│   ├── fusion/                    # Data and decision fusion modules
│   ├── resilience/                # Fault tolerance and recovery logic
│   ├── explainability/            # Interpretability and audit trails
│   └── benchmarking/              # Performance evaluation and metrics
│
├── astra/                         # ASTRA subsystem (verbatim copy)
│   ├── src/                       # ASTRA core source code
│   ├── configs/                   # ASTRA configuration files
│   ├── dashboard/                 # ASTRA dashboard UI
│   ├── data/                      # ASTRA local data
│   ├── docs/                      # ASTRA documentation
│   ├── logs/                      # ASTRA log output
│   ├── models_store/              # ASTRA trained models
│   ├── notebooks/                 # ASTRA Jupyter notebooks
│   ├── requirements.txt           # ASTRA Python dependencies
│   ├── requirements-lock.txt      # ASTRA pinned dependencies
│   ├── system_documentation.md    # ASTRA system docs
│   └── README.md                  # ASTRA readme
│
├── scade/                         # SCADE subsystem (verbatim copy)
│   ├── src/                       # SCADE core source code
│   ├── app/                       # SCADE application layer
│   ├── config/                    # SCADE configuration
│   ├── data/                      # SCADE local data
│   ├── models/                    # SCADE model definitions
│   ├── main.py                    # SCADE entry point
│   ├── run.py                     # SCADE runner script
│   ├── start.py                   # SCADE startup script
│   ├── requirements.txt           # SCADE Python dependencies
│   ├── SCADE_TECHNICAL_SPECIFICATION.md  # SCADE technical spec
│   └── README.md                  # SCADE readme
│
├── data/                          # Shared data directory for SCADE-X
│   ├── raw/                       # Unprocessed input data
│   ├── processed/                 # Final processed outputs
│   └── intermediate/              # Mid-pipeline intermediate artifacts
│
├── outputs/                       # Pipeline outputs, reports, results
│
├── configs/                       # Unified SCADE-X configuration files
│
├── main.py                        # SCADE-X top-level entry point
├── requirements.txt               # SCADE-X consolidated dependencies
└── README.md                      # Project overview and quickstart
```

---

## 3. Folder Purposes

### 3.1 `docs/`

Project-level documentation for SCADE-X. Houses this structure document and will contain architecture diagrams, API specifications, and design decision records as the project evolves.

### 3.2 `src/` — Integration Source Code

The core SCADE-X integration logic lives here. Each subdirectory is a distinct concern:

| Directory | Intended Purpose |
|-----------|-----------------|
| `src/orchestration/` | The central nervous system of SCADE-X. Will contain pipeline definitions, task scheduling, and workflow management that coordinate ASTRA and SCADE subsystems. |
| `src/fusion/` | Data and decision fusion modules. Responsible for combining outputs from both subsystems — sensor fusion, confidence merging, and cross-system correlation. |
| `src/resilience/` | Fault tolerance, failover strategies, circuit breakers, and graceful degradation. Ensures the integrated system continues operating when individual subsystems fail. |
| `src/explainability/` | Interpretability modules that provide audit trails, decision explanations, and transparency into the integrated pipeline's reasoning process. |
| `src/benchmarking/` | Performance evaluation, latency profiling, accuracy metrics, and comparative analysis between subsystem outputs and the fused result. |

### 3.3 `astra/` — ASTRA Subsystem

**Verbatim copy** of the original `ASTRA/` repository. Contains the full ASTRA source tree including its own `src/`, `configs/`, `dashboard/`, data directories, model store, notebooks, and documentation.

> ⚠️ **No modifications have been made.** All imports, paths, and configurations remain as they were in the original ASTRA repository.

### 3.4 `scade/` — SCADE Subsystem

**Verbatim copy** of the original `SCADE/` repository. Contains the full SCADE source tree including its own `src/`, `app/`, `config/`, model definitions, and entry points (`main.py`, `run.py`, `start.py`).

> ⚠️ **No modifications have been made.** All imports, paths, and configurations remain as they were in the original SCADE repository.

### 3.5 `data/` — Shared Data Directory

A three-tier data pipeline directory for SCADE-X's integration layer:

| Directory | Purpose |
|-----------|---------|
| `data/raw/` | Unprocessed input data fed into the integrated pipeline. Source data before any transformation. |
| `data/intermediate/` | Mid-pipeline artifacts produced during processing. Outputs from one stage that feed into the next. |
| `data/processed/` | Final, fully processed data ready for downstream consumption or reporting. |

> **Note:** Each subsystem retains its own `data/` directory internally. This shared `data/` is exclusively for the SCADE-X integration layer.

### 3.6 `outputs/`

Final pipeline outputs, generated reports, visualizations, and results produced by the SCADE-X orchestration layer. Kept separate from `data/` to distinguish between in-pipeline data and deliverable artifacts.

### 3.7 `configs/`

Unified configuration files for the SCADE-X integration layer. Will contain orchestration settings, fusion parameters, resilience thresholds, and cross-system configuration. Subsystem-specific configs remain in their respective `astra/configs/` and `scade/config/` directories.

---

## 4. Copied Components

| Source | Destination | Method |
|--------|-------------|--------|
| `ISR Systems/ASTRA/*` | `SCADE-X/astra/` | Recursive copy (`cp -a`) preserving all attributes |
| `ISR Systems/SCADE/*` | `SCADE-X/scade/` | Recursive copy (`cp -a`) preserving all attributes |

Both copies include all source code, configuration, data, documentation, and metadata files. Hidden files (`.gitignore`, `.env`) were preserved. The `.git/` directories from both subsystems were included to maintain version history reference.

---

## 5. Preserved Subsystem Boundaries

The following integrity guarantees are maintained:

1. **No code modifications** — Zero lines of ASTRA or SCADE source code were altered.
2. **No import rewrites** — All internal imports within each subsystem remain exactly as they were in the original repositories.
3. **No configuration changes** — Config files, environment variables, and path references are untouched.
4. **Independent runnability** — Each subsystem can still be run independently from within its own directory (`astra/` or `scade/`), using its own entry points and requirements.
5. **Isolated dependencies** — Each subsystem's `requirements.txt` is preserved. The top-level `requirements.txt` is a placeholder for future SCADE-X-specific dependencies.

---

## 6. Design Rationale

### Why copy instead of symlink?
Copies ensure that SCADE-X is a fully self-contained project. Symlinks would create fragile dependencies on the original directory layout and could break if the parent repository is reorganized.

### Why preserve `.git/` directories?
Retaining git history within the subsystem directories allows developers to trace the provenance of any subsystem code back to its original commits, without requiring access to the parent repository.

### Why separate `src/` from `astra/` and `scade/`?
The `src/` directory is exclusively for **new integration code** written as part of SCADE-X. Keeping it separate from the subsystem directories enforces a clear architectural boundary: SCADE-X orchestrates and extends — it does not modify the subsystems.

---

## 7. Next Steps

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 1 | Scaffold & copy subsystems | ✅ Complete |
| Phase 2 | Orchestration logic in `src/orchestration/` | ⬜ Pending |
| Phase 3 | Fusion pipeline in `src/fusion/` | ⬜ Pending |
| Phase 4 | Resilience & explainability | ⬜ Pending |
| Phase 5 | Benchmarking & evaluation | ⬜ Pending |
