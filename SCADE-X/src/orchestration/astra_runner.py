"""
SCADE-X ASTRA Runner
====================
Orchestrates the ASTRA pipeline execution as a black box.
Runs ASTRA modules in correct order and collects generated artifacts.
Supports fallback entrypoints, robust pathing, and detailed diagnostic reporting.
"""
import subprocess
import os
import sys
import re
from pathlib import Path
from src.orchestration.execution_context import ExecutionContext
from src.orchestration.artifact_manager import ArtifactManager

class ASTRARunner:
    def __init__(self, ctx: ExecutionContext, artifact_mgr: ArtifactManager):
        self.ctx = ctx
        self.artifact_mgr = artifact_mgr
        self.astra_dir = (self.artifact_mgr.base_dir / "astra").resolve()
        self.logger = self.ctx.logger.getChild("ASTRA_Runner")
        
    def _register_expected_artifacts(self):
        """Registers the expected outputs from the ASTRA pipeline."""
        artifacts = {
            "workflow_sequences": "data/processed/workflow_sequences.json",
            "process_vocab": "data/processed/process_vocab.json",
            "tokenized_sequences": "data/processed/tokenized_sequences.json",
            "process_transformer_model": "models_store/process_transformer.pth",
            "process_features": "data/processed/process_features.csv",
            "isolation_results": "data/processed/isolation_forest_results.csv",
            "supply_chain_graph": "data/processed/supply_chain_graph.gpickle",
            "graph_features": "data/processed/graph_features.csv",
            "transformer_scores": "data/processed/transformer_scores.json",
            "fusion_scores": "data/processed/fused_risk_scores.csv",
            "benchmark_results": "data/processed/model_benchmark.csv",
            "explainability_report": "data/processed/explainability_report.txt"
        }
        for name, rel_path in artifacts.items():
            self.artifact_mgr.register_astra_artifact(name, rel_path)
            
    def _detect_missing_dependency(self, stderr: str) -> str:
        """Parses stderr to detect missing dependencies and returns a suggestion."""
        # Common module-to-pip mapping for suggestion
        pip_map = {
            "pm4py": "pm4py",
            "pandas": "pandas",
            "numpy": "numpy",
            "sklearn": "scikit-learn",
            "networkx": "networkx",
            "torch": "torch",
            "matplotlib": "matplotlib",
            "seaborn": "seaborn",
            "yaml": "pyyaml",
            "flask": "flask"
        }
        match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", stderr)
        if not match:
            match = re.search(r"ImportError: No module named ([^\s\n]+)", stderr)
        if match:
            mod = match.group(1).split(".")[0]
            pip_pkg = pip_map.get(mod, mod)
            return f"Missing dependency: {mod}. Recommended fix: pip install {pip_pkg}"
        return ""

    def execute(self) -> bool:
        """
        Executes the ASTRA pipeline using a robust entrypoint fallback logic.
        """
        state = self.ctx.get_subsystem_state("ASTRA")
        state.mark_running()
        self.logger.info("Starting ASTRA subsystem execution.")
        
        self._register_expected_artifacts()
        
        # fallback entrypoints configuration in order:
        # format: (description, cwd_path, cmd_args, env_overrides, check_file_exists)
        fallbacks = [
            (
                "Root main.py", 
                self.astra_dir, 
                [sys.executable, "main.py"], 
                {}, 
                self.astra_dir / "main.py"
            ),
            (
                "Source folder main.py", 
                self.astra_dir, 
                [sys.executable, "src/main.py"], 
                {"PYTHONPATH": "src"}, 
                self.astra_dir / "src/main.py"
            ),
            (
                "Module run src.main", 
                self.astra_dir, 
                [sys.executable, "-m", "src.main"], 
                {"PYTHONPATH": "."}, 
                self.astra_dir / "src/main.py"
            ),
            (
                "Nested run inside src/", 
                self.astra_dir / "src", 
                [sys.executable, "main.py"], 
                {}, 
                self.astra_dir / "src/main.py"
            ),
        ]
        
        executed = False
        last_error = None
        
        for name, cwd, cmd, env_adds, check_file in fallbacks:
            if not check_file.exists():
                self.logger.debug(f"ASTRA Entrypoint [{name}] skipped: check file {check_file} does not exist.")
                continue
                
            self.logger.info(f"Attempting ASTRA entrypoint [{name}]...")
            self.logger.info(f"Command: {' '.join(cmd)}")
            self.logger.info(f"Working Directory: {cwd}")
            
            # Setup environment variables
            env = os.environ.copy()
            for k, v in env_adds.items():
                env[k] = v
                
            try:
                result = subprocess.run(
                    cmd,
                    cwd=str(cwd),
                    env=env,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.logger.info(f"ASTRA entrypoint [{name}] executed successfully.")
                    self.logger.debug(f"ASTRA stdout: {result.stdout}")
                    executed = True
                    break
                else:
                    err_msg = (
                        f"ASTRA entrypoint [{name}] failed with exit code {result.returncode}.\n"
                        f"Stdout: {result.stdout.strip()}\n"
                        f"Stderr: {result.stderr.strip()}"
                    )
                    self.logger.warning(err_msg)
                    last_error = {
                        "cmd": cmd,
                        "cwd": cwd,
                        "exit_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }
            except Exception as e:
                self.logger.warning(f"ASTRA entrypoint [{name}] raised exception: {e}")
                last_error = {
                    "cmd": cmd,
                    "cwd": cwd,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": str(e)
                }

        if executed:
            state.mark_completed()
            self.logger.info("ASTRA subsystem execution completed successfully.")
            return True
        else:
            state.mark_failed(str(last_error))
            self.logger.error("=" * 60)
            self.logger.error("ASTRA SUBSYSTEM EXECUTION FAILED")
            self.logger.error("=" * 60)
            
            if last_error:
                cmd_str = " ".join(last_error["cmd"])
                self.logger.error(f"Last Attempted Script : {cmd_str}")
                self.logger.error(f"Working Directory     : {last_error['cwd']}")
                self.logger.error(f"Exit Code             : {last_error['exit_code']}")
                self.logger.error("-" * 60)
                self.logger.error(f"STDOUT:\n{last_error['stdout']}")
                self.logger.error("-" * 60)
                self.logger.error(f"STDERR:\n{last_error['stderr']}")
                self.logger.error("-" * 60)
                
                # Try to diagnose missing dependencies
                dep_suggestion = self._detect_missing_dependency(last_error["stderr"])
                if dep_suggestion:
                    self.logger.error(f"Detected Issue        : {dep_suggestion}")
                else:
                    self.logger.error("Detected Issue        : Internal subsystem runtime crash.")
                self.logger.error("Recommended Fix       : Resolve environment issues shown in stderr above.")
            else:
                self.logger.error("No valid ASTRA entrypoint script could be found.")
                self.logger.error("Recommended Fix       : Ensure ASTRA folder is populated and has a main.py entrypoint.")
                
            self.logger.error("=" * 60)
            
            raise RuntimeError("ASTRA execution failed internally (hardened check).")

    def get_outputs(self) -> dict:
        """Returns the dictionary of tracked ASTRA artifacts."""
        return self.artifact_mgr.get_astra_artifacts()
