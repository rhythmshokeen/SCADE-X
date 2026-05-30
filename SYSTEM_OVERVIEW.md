# ISR Systems - Comprehensive Project Overview

This document provides a holistic overview of the entire **ISR Systems** project. It details the purpose of each main directory, the files they contain, and the exact end-to-end execution workflow of the system.

## 1. Project Structure & Directory Purposes

The ISR Systems root directory is structured into three primary repositories/subsystems:

### 1. `ASTRA/` (Threat Recognition & Analysis)
This subsystem focuses on the security context and threat intelligence.
- **`src/`**: Contains the source code for the ASTRA AI models and processing logic.
- **`configs/`**: Stores configuration files required for the ASTRA subsystem.
- **`models_store/`**: Contains trained or downloaded machine learning models used by ASTRA.
- **`dashboard/`**: Contains code for a web-based or visual dashboard to display ASTRA analytics.
- **`notebooks/`**: Jupyter notebooks for experimentation and analysis.
- **`data/`, `logs/`, `docs/`**: Subdirectories for datasets, execution logs, and ASTRA-specific documentation (e.g., `system_documentation.md`).
- **`requirements.txt` / `requirements-lock.txt`**: Dependency definitions.

### 2. `SCADE/` (Supply Chain Anomaly Detection & Evaluation)
This is the core subsystem for identifying supply chain anomalies and conformance checking.
- **`main.py`, `run.py`, `start.py`**: Multiple entry points to execute the SCADE pipeline independently.
- **`src/`**: The core source code for SCADE's algorithms, anomaly detection logic, and risk assessment.
- **`models/`**: Predictive models tailored for supply chain anomaly detection.
- **`app/`**: A potential web application or API service layer for SCADE.
- **`config/`**: Configuration for running SCADE.
- **`data/`**: Stores input datasets and output results from SCADE execution.
- **`SCADE_TECHNICAL_SPECIFICATION.md`**: Deep technical documentation for this module.

### 3. `SCADE-X/` (Unified End-to-End Pipeline & Orchestrator)
This is the overarching umbrella that integrates both ASTRA and SCADE into a unified intelligence engine.
- **`main.py`**: The primary CLI entry point for the entire unified system. This is where execution begins.
- **`src/orchestration/`**: Contains the pipeline definition (`scadex_pipeline.py`) and runners that execute ASTRA and SCADE subsystems as black boxes.
- **`src/fusion/`**: Contains `SchemaNormalizer` and `IntelligenceFusionEngine` to merge insights from ASTRA and SCADE.
- **`src/resilience/`**: Contains `ResilienceEngine` to compute overall system robustness based on the data.
- **`src/explainability/`**: Contains `XAIEngine` for generating human-readable explanations of the fused decisions.
- **`src/benchmarking/`**: Framework to evaluate the system mathematically and practically.
- **`outputs/`**: The final destination for all fused reports, explanations, and intelligence artifacts.
- **`configs/`**, **`docs/`**, **`data/`**: Configuration, comprehensive documentation, and intermediate data.

---

## 2. System Workflow (End-to-End Execution Flow)

The ISR system operates as a unified pipeline driven by **SCADE-X**. The exact chronological workflow is as follows:

1. **Initialization & Setup**:
   - Execution begins by running `SCADE-X/main.py`.
   - The orchestrator generates a unique Run ID, loads the overarching configuration (`scadex_config.yaml`), and sets up output directories for logs, reports, and intelligence.

2. **Input & Environment Validation**:
   - The system checks if required data logs (procurement, security, etc.) are available in the expected paths.
   - It validates Python environments and dependencies to ensure subsystems can run smoothly.

3. **ASTRA Subsystem Execution**:
   - The orchestrator triggers the `ASTRA` subsystem (located in the `ASTRA/` folder) through a dedicated runner.
   - ASTRA processes security/threat logs and produces its own outputs (e.g., threat scores), saving them as intermediate artifacts.

4. **SCADE Subsystem Execution**:
   - The orchestrator triggers the `SCADE` subsystem (located in the `SCADE/` folder) using robust fallback entry points (`main.py`, `run.py`, or `start.py`).
   - SCADE processes procurement logs, running its anomaly detection models, and outputs conformance and risk scores.

5. **Schema Normalization**:
   - With both subsystems finished, the `SCADE-X` orchestrator passes the output artifacts to the `SchemaNormalizer`.
   - The normalizer standardizes the differing data structures from ASTRA and SCADE so they can be merged.

6. **Resilience Intelligence**:
   - The `ResilienceEngine` analyzes the normalized system data to compute robustness and resilience metrics against potential disruptions or threats.

7. **Intelligence Fusion**:
   - The `IntelligenceFusionEngine` aggregates the normalized threat scores (from ASTRA), anomaly risk scores (from SCADE), and resilience metrics into a single, cohesive composite intelligence picture.

8. **Explainability Generation (XAI)**:
   - The `XAIEngine` processes the fused intelligence data to generate automated, human-readable explanations. It provides justifications for *why* an anomaly was flagged or a risk score was assigned.

9. **Benchmarking & Evaluation**:
   - The `SCADEXBenchmark` framework mathematically evaluates the entire pipeline's performance and accuracy, ensuring the results meet required standards.

10. **Artifact Export**:
    - Finally, the pipeline exports all processed artifacts (composite intelligence, resilience reports, benchmark summaries, and explanations) to the user-facing `SCADE-X/outputs/` directory.
    - The orchestrator logs a final success message, and execution completes.
