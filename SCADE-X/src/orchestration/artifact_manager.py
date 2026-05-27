"""
SCADE-X Artifact Manager
========================
Central registry for tracking input files, intermediate outputs,
model paths, and final outputs across both ASTRA and SCADE subsystems.
"""
from typing import Dict, Any, List
from pathlib import Path

class ArtifactManager:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.artifacts: Dict[str, Dict[str, Path]] = {
            "inputs": {},
            "astra": {},
            "scade": {},
            "scade_x": {}
        }
        
    def register_input(self, name: str, path: str):
        full_path = self.base_dir / path
        self.artifacts["inputs"][name] = full_path
        
    def register_astra_artifact(self, name: str, relative_path: str):
        full_path = self.base_dir / "astra" / relative_path
        self.artifacts["astra"][name] = full_path
        
    def register_scade_artifact(self, name: str, relative_path: str):
        full_path = self.base_dir / "scade" / relative_path
        self.artifacts["scade"][name] = full_path
        
    def get_astra_artifacts(self) -> Dict[str, Path]:
        """Returns key ASTRA artifacts based on architectural mapping."""
        return self.artifacts.get("astra", {})
        
    def get_scade_artifacts(self) -> Dict[str, Path]:
        """Returns key SCADE artifacts based on architectural mapping."""
        return self.artifacts.get("scade", {})

    def verify_artifacts(self, subsystem: str, required_keys: List[str]) -> bool:
        """Verifies that all required artifacts for a subsystem exist on disk."""
        if subsystem not in self.artifacts:
            return False
            
        all_exist = True
        for key in required_keys:
            path = self.artifacts[subsystem].get(key)
            if not path or not path.exists():
                all_exist = False
        return all_exist
