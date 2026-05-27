"""
SCADE-X SCADE Runner
====================
Orchestrates the SCADE pipeline execution as a black box.
Runs SCADE modules and collects outputs.
Supports fallback entrypoints, robust pathing, and detailed diagnostic reporting.
"""
import subprocess
import os
import sys
import re
from pathlib import Path
from src.orchestration.execution_context import ExecutionContext
from src.orchestration.artifact_manager import ArtifactManager

class SCADERunner:
    def __init__(self, ctx: ExecutionContext, artifact_mgr: ArtifactManager):
        self.ctx = ctx
        self.artifact_mgr = artifact_mgr
        self.scade_dir = (self.artifact_mgr.base_dir / "scade").resolve()
        self.logger = self.ctx.logger.getChild("SCADE_Runner")
        
    def _register_expected_artifacts(self):
        """Registers the expected outputs from the SCADE pipeline."""
        artifacts = {
            "cf_score": "data/conformance_flow.csv",
            "time_score": "data/conformance_time.csv",
            "resource_score": "data/conformance_resource.csv",
            "amount_score": "data/conformance_amount.csv",
            "security_score": "data/conformance_security.csv",
            "fusion_scores": "data/composite_scores.csv",
            "attack_mapping": "data/attack_mappings.csv",
            "supplier_risk": "data/supplier_risk.csv",
            "user_risk": "data/user_risk.csv",
            "explainability_outputs": "data/explanations.json"
        }
        for name, rel_path in artifacts.items():
            self.artifact_mgr.register_scade_artifact(name, rel_path)
            
    def _detect_missing_dependency(self, stderr: str) -> str:
        """Parses stderr to detect missing dependencies and returns a suggestion."""
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
        Executes the SCADE pipeline using a robust entrypoint fallback logic.
        """
        state = self.ctx.get_subsystem_state("SCADE")
        state.mark_running()
        self.logger.info("Starting SCADE subsystem execution.")
        
        self._register_expected_artifacts()
        
        # fallback entrypoints inside scade_dir:
        # format: (description, cwd_path, cmd_args, env_overrides, check_file_exists)
        fallbacks = [
            (
                "main.py", 
                self.scade_dir, 
                [sys.executable, "main.py"], 
                {}, 
                self.scade_dir / "main.py"
            ),
            (
                "run.py", 
                self.scade_dir, 
                [sys.executable, "run.py"], 
                {}, 
                self.scade_dir / "run.py"
            ),
            (
                "start.py", 
                self.scade_dir, 
                [sys.executable, "start.py"], 
                {}, 
                self.scade_dir / "start.py"
            )
        ]
        
        executed = False
        last_error = None
        
        for name, cwd, cmd, env_adds, check_file in fallbacks:
            if not check_file.exists():
                self.logger.debug(f"SCADE Entrypoint [{name}] skipped: check file {check_file} does not exist.")
                continue
                
            self.logger.info(f"Executing SCADE entrypoint script: {name}...")
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
                    self.logger.info(f"SCADE entrypoint [{name}] executed successfully.")
                    self.logger.debug(f"SCADE stdout: {result.stdout}")
                    executed = True
                    break
                else:
                    err_msg = (
                        f"SCADE entrypoint [{name}] failed with exit code {result.returncode}.\n"
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
                self.logger.warning(f"SCADE entrypoint [{name}] raised exception: {e}")
                last_error = {
                    "cmd": cmd,
                    "cwd": cwd,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": str(e)
                }

        if executed:
            state.mark_completed()
            self.logger.info("SCADE subsystem execution completed successfully.")
            return True
        else:
            state.mark_failed(str(last_error))
            self.logger.error("=" * 60)
            self.logger.error("SCADE SUBSYSTEM EXECUTION FAILED")
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
                self.logger.error("No valid SCADE entrypoint script could be found.")
                self.logger.error("Recommended Fix       : Ensure SCADE folder contains main.py, run.py, or start.py.")
                
            self.logger.error("=" * 60)
            
            raise RuntimeError("SCADE execution failed internally (hardened check).")

    def get_outputs(self) -> dict:
        """Returns the dictionary of tracked SCADE artifacts."""
        return self.artifact_mgr.get_scade_artifacts()
