"""
SCADE-X Execution Context
=========================
Manages runtime configuration, execution metadata, subsystem states,
and pipeline logging for the integrated SCADE-X orchestration layer.
"""
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class SubsystemState:
    name: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    start_time: float = 0.0
    end_time: float = 0.0
    error_message: Optional[str] = None
    
    def mark_running(self):
        self.status = "RUNNING"
        self.start_time = time.time()
        
    def mark_completed(self):
        self.status = "COMPLETED"
        self.end_time = time.time()
        
    def mark_failed(self, error: str):
        self.status = "FAILED"
        self.error_message = error
        self.end_time = time.time()
        
    @property
    def duration_sec(self) -> float:
        if self.start_time == 0.0:
            return 0.0
        end = self.end_time if self.end_time > 0.0 else time.time()
        return end - self.start_time


class ExecutionContext:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.start_time = time.time()
        self.end_time = 0.0
        self.status = "INITIALIZED"
        self.states: Dict[str, SubsystemState] = {
            "ASTRA": SubsystemState(name="ASTRA"),
            "SCADE": SubsystemState(name="SCADE")
        }
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"SCADE-X-{self.run_id}")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        )
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(ch)
        return logger
        
    def get_subsystem_state(self, name: str) -> SubsystemState:
        return self.states.get(name)
        
    def mark_pipeline_completed(self):
        self.status = "COMPLETED"
        self.end_time = time.time()
        self.logger.info(f"Pipeline {self.run_id} completed in {self.end_time - self.start_time:.2f}s")
        
    def mark_pipeline_failed(self, reason: str):
        self.status = "FAILED"
        self.end_time = time.time()
        self.logger.error(f"Pipeline {self.run_id} failed: {reason}")
