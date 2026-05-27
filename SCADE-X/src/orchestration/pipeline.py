"""
SCADE-X Pipeline Orchestrator
=============================
Main integration entry point that wraps and orchestrates ASTRA and SCADE.
Defines the execution boundaries, triggers subsystems, and unifies output context.
"""
import uuid
import sys
from pathlib import Path
from src.orchestration.execution_context import ExecutionContext
from src.orchestration.artifact_manager import ArtifactManager
from src.orchestration.astra_runner import ASTRARunner
from src.orchestration.scade_runner import SCADERunner

class SCADEXPipeline:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
        self.run_id = str(uuid.uuid4())[:8]
        self.ctx = ExecutionContext(self.run_id)
        self.artifact_mgr = ArtifactManager(self.base_dir)
        
        # Initialize runners
        self.astra = ASTRARunner(self.ctx, self.artifact_mgr)
        self.scade = SCADERunner(self.ctx, self.artifact_mgr)
        
    def register_inputs(self, procurement_log: str, security_log: str):
        """Registers global input files to be used by the orchestration layer."""
        self.artifact_mgr.register_input("procurement_log", procurement_log)
        self.artifact_mgr.register_input("security_log", security_log)
        self.ctx.logger.info("Inputs registered in ArtifactManager.")

    def run(self) -> ExecutionContext:
        """
        Orchestrates the sequential/parallel execution of the integrated pipeline.
        Currently executes sequentially to safely manage resources.
        """
        self.ctx.logger.info("=== SCADE-X Orchestration Pipeline Started ===")
        
        # 1. Execute ASTRA Subsystem
        astra_success = self.astra.execute()
        if not astra_success:
            self.ctx.mark_pipeline_failed("ASTRA execution failed.")
            return self.ctx
            
        # 2. Execute SCADE Subsystem
        scade_success = self.scade.execute()
        if not scade_success:
            self.ctx.mark_pipeline_failed("SCADE execution failed.")
            return self.ctx
            
        # 3. Collection & Unification (Prepared for future Fusion logic)
        self._collect_subsystem_outputs()
        
        self.ctx.mark_pipeline_completed()
        return self.ctx
        
    def _collect_subsystem_outputs(self):
        """Logs the collected artifacts from both subsystems."""
        astra_artifacts = self.astra.get_outputs()
        scade_artifacts = self.scade.get_outputs()
        
        self.ctx.logger.info("--- ASTRA Artifacts Generated ---")
        for k, v in astra_artifacts.items():
            self.ctx.logger.info(f"{k}: {v}")
            
        self.ctx.logger.info("--- SCADE Artifacts Generated ---")
        for k, v in scade_artifacts.items():
            self.ctx.logger.info(f"{k}: {v}")

if __name__ == "__main__":
    # Example standalone execution test
    pipeline = SCADEXPipeline(base_dir=".")
    pipeline.register_inputs(
        procurement_log="data/raw/synthetic_supply_chain.csv",
        security_log="data/raw/security.csv"
    )
    context = pipeline.run()
    
    if context.status == "COMPLETED":
        print("SCADE-X Pipeline finished successfully.")
    else:
        print("SCADE-X Pipeline encountered an error.")
        sys.exit(1)
