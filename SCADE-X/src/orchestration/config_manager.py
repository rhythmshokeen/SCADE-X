"""
SCADE-X Config Manager
======================
Loads YAML configurations and applies CLI argument overrides.
"""
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "configs/scadex_config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load()
        
    def _load(self):
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {
                "pipeline": {"run_astra": True, "run_scade": True, "run_benchmarks": True, "debug_mode": False},
                "paths": {"input_log": "data/raw/synthetic_supply_chain.csv", "security_log": "data/raw/security.csv", "output_dir": "outputs"}
            }

    def override_from_cli(self, args):
        if args.input:
            self.config["paths"]["input_log"] = args.input
        if args.security_log:
            self.config["paths"]["security_log"] = args.security_log
        if args.skip_benchmark:
            self.config["pipeline"]["run_benchmarks"] = False
        if args.debug:
            self.config["pipeline"]["debug_mode"] = True
        if args.output_dir:
            self.config["paths"]["output_dir"] = args.output_dir

    def get(self, section: str, key: str = None) -> Any:
        sec = self.config.get(section, {})
        if key:
            return sec.get(key)
        return sec
