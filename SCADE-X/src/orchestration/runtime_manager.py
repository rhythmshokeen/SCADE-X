"""
SCADE-X Runtime Manager
=======================
Tracks the execution lifecycle, manages stage transitions, handles
failure recovery, and computes runtime statistics.
"""
import time
import logging
from typing import Dict, Any
from src.orchestration.execution_context import ExecutionContext

class RuntimeManager:
    def __init__(self, run_id: str, logger: logging.Logger):
        self.run_id = run_id
        self.logger = logger
        self.ctx = ExecutionContext(run_id)
        self.stages: Dict[str, Dict[str, Any]] = {}
        self.global_start = time.time()
        
    def start_stage(self, stage_name: str):
        self.logger.info(f"=== Starting Stage: {stage_name} ===")
        self.stages[stage_name] = {
            "start": time.time(),
            "status": "RUNNING",
            "end": None,
            "error": None
        }
        
    def complete_stage(self, stage_name: str):
        if stage_name in self.stages:
            self.stages[stage_name]["end"] = time.time()
            self.stages[stage_name]["status"] = "COMPLETED"
            duration = self.stages[stage_name]["end"] - self.stages[stage_name]["start"]
            self.logger.info(f"=== Completed Stage: {stage_name} (Duration: {duration:.2f}s) ===")
            
    def fail_stage(self, stage_name: str, error: Exception) -> bool:
        """Records failure. Returns True if pipeline should abort."""
        if stage_name in self.stages:
            self.stages[stage_name]["end"] = time.time()
            self.stages[stage_name]["status"] = "FAILED"
            self.stages[stage_name]["error"] = str(error)
            
        self.logger.error(f"!!! Stage Failed: {stage_name} !!!")
        self.logger.error(f"Error: {error}")
        
        # Determine if we can recover or skip. 
        # For SCADE-X, missing benchmark is recoverable. Missing Fusion is fatal.
        if stage_name == "Benchmarking":
            self.logger.warning("Benchmarking failed. Recovering and continuing pipeline.")
            return False
        return True

    def summarize(self):
        self.logger.info("=== SCADE-X Runtime Summary ===")
        for stage, data in self.stages.items():
            dur = data["end"] - data["start"] if data["end"] else 0.0
            status = data["status"]
            self.logger.info(f"Stage: {stage:<20} | Status: {status:<10} | Time: {dur:.2f}s")
        
        total_time = time.time() - self.global_start
        self.logger.info(f"Total Pipeline Execution Time: {total_time:.2f}s")
