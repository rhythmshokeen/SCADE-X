#!/usr/bin/env python3
"""
SCADE-X Main Entry Point
========================
Provides the CLI interface to execute the unified End-to-End
SCADE-X execution pipeline.
"""
import argparse
from pathlib import Path
from src.orchestration.config_manager import ConfigManager
from src.orchestration.scadex_pipeline import SCADEXUnifiedPipeline

def parse_args():
    parser = argparse.ArgumentParser(description="SCADE-X End-to-End Intelligence Pipeline")
    parser.add_argument("--input", type=str, help="Path to primary procurement event log.")
    parser.add_argument("--security-log", type=str, help="Path to SIEM security context log.")
    parser.add_argument("--skip-benchmark", action="store_true", help="Skips rigorous mathematical evaluation.")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging.")
    parser.add_argument("--output-dir", type=str, help="Custom output directory for artifacts.")
    parser.add_argument("--config", type=str, default="configs/scadex_config.yaml", help="Path to custom YAML config.")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # 1. Load config
    config = ConfigManager(args.config)
    
    # 2. Apply CLI overrides
    config.override_from_cli(args)
    
    # 3. Initialize and Execute Pipeline
    base_dir = Path(__file__).resolve().parent
    pipeline = SCADEXUnifiedPipeline(str(base_dir), config)
    pipeline.execute()

if __name__ == "__main__":
    main()
