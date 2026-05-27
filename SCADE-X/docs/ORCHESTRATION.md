# SCADE-X Orchestration Architecture

This document outlines the design and operation of the SCADE-X integration orchestration layer, which serves as the unified entry point for executing both the ASTRA and SCADE subsystems without modifying their internal logic.

## 1. Orchestration Design

The orchestration layer is designed around a **Black-Box Wrapping** philosophy. ASTRA and SCADE are treated as independent microservices that communicate purely through standard input data and well-defined output artifacts. 

The core components live in `src/orchestration/`:
- `execution_context.py`: Maintains the global state of the pipeline, tracks execution times, and handles centralized logging.
- `artifact_manager.py`: Serves as the central registry mapping logical artifact names (e.g., `transformer_scores`) to their physical paths on disk.
- `astra_runner.py`: Wrapper for the ASTRA subsystem.
- `scade_runner.py`: Wrapper for the SCADE subsystem.
- `pipeline.py`: The top-level orchestrator that coordinates the runners and the context.

## 2. Execution Order

The `SCADEXPipeline.run()` method orchestrates execution in the following linear flow:

1. **Input Registration**: Raw procurement and security logs are registered with the `ArtifactManager`.
2. **ASTRA Execution**: 
   - `ASTRARunner` initializes and registers its expected outputs.
   - It invokes `astra/main.py` inside an isolated subprocess using the ASTRA directory as the working directory.
   - It captures logs and marks the subsystem state as `COMPLETED` or `FAILED`.
3. **SCADE Execution**:
   - `SCADERunner` initializes and registers its expected outputs.
   - It invokes `scade/main.py` inside an isolated subprocess using the SCADE directory as the working directory.
   - It captures logs and updates the execution context.
4. **Artifact Collection & Unification**: The outputs from both subsystems are logged and readied for the future Fusion layer.

*Note: Sequential execution is currently enforced to prevent memory constraints (e.g., PyTorch models in ASTRA and PM4Py models in SCADE running simultaneously), though the architecture supports asynchronous parallel execution.*

## 3. Wrapper Interfaces

Both `ASTRARunner` and `SCADERunner` implement a consistent interface:

- `execute() -> bool`: Triggers the underlying subsystem by spawning a Python subprocess targeting the system's entry script (`main.py`). This guarantees environment isolation and preserves subsystem integrity (no path collision or import errors).
- `get_outputs() -> dict`: Interrogates the `ArtifactManager` to return a dictionary mapping logical output names to their physical `Path` objects.

By using `subprocess.run(cwd=...)`, the wrapper strictly enforces the requirement that both ASTRA and SCADE remain independently runnable exactly as they were before integration.

## 4. Artifact Lifecycle

Artifacts are managed centrally by the `ArtifactManager`.

1. **Registration**: Before a subsystem runs, the runner registers the expected relative paths of all artifacts (e.g., `data/processed/process_features.csv` for ASTRA).
2. **Generation**: The black-box execution of the subsystem generates the actual files on disk.
3. **Validation**: After execution, the orchestration layer can verify the presence of these artifacts.
4. **Consumption**: Downstream modules (like the future SCADE-X Fusion engine) request artifacts via logical names (e.g., `artifact_mgr.get_astra_artifacts()["fusion_scores"]`) instead of hardcoding paths.

## 5. Subsystem Interaction Model

The subsystems **do not interact directly** with each other. 

ASTRA does not know about SCADE's conformance engine, and SCADE does not know about ASTRA's transformer. They both consume the same input logs, process them using their respective intelligence pipelines, and dump their artifacts. The `SCADEXPipeline` acts as the overarching broker that collects these artifacts and will pass them to `src/fusion/meta_fusion.py` in the next phase.

## 6. Failure Handling

Resilience is built directly into the orchestration bounds:

- **Isolated Failures**: Because subsystems run as isolated subprocesses, a crash in SCADE (e.g., PM4Py Inductive Miner deadlock) will not crash the Python process running the ASTRA transformer.
- **State Tracking**: `ExecutionContext` uses a `SubsystemState` data class to track `PENDING`, `RUNNING`, `COMPLETED`, or `FAILED` states, along with execution durations.
- **Traceable Errors**: `stderr` and `stdout` from the subprocesses are captured and logged to the central `SCADE-X-{run_id}` logger.
- **Circuit Breaking**: If ASTRA fails, the pipeline logs the failure in the context and safely aborts (or continues depending on future resilience configuration) before triggering dependent downstream operations.
