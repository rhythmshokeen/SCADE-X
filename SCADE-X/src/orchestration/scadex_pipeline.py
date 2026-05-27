"""
SCADE-X Unified Pipeline
========================
The top-level execution flow that sequentially orchestrates all SCADE-X layers.
"""
import sys
import uuid
import shutil
from pathlib import Path

from src.orchestration.config_manager import ConfigManager
from src.orchestration.logger import setup_logger
from src.orchestration.runtime_manager import RuntimeManager
from src.orchestration.artifact_manager import ArtifactManager
from src.orchestration.environment_validator import validate_environment

# Import subsystem runners
from src.orchestration.astra_runner import ASTRARunner
from src.orchestration.scade_runner import SCADERunner

# Import execution modules
from src.fusion.schema_normalizer import SchemaNormalizer
from src.resilience.resilience_engine import ResilienceEngine
from src.fusion.intelligence_fusion import IntelligenceFusionEngine
from src.explainability.xai_engine import XAIEngine
from src.benchmarking.scadex_benchmark import SCADEXBenchmark

class SCADEXUnifiedPipeline:
    def __init__(self, base_dir: str, config: ConfigManager):
        self.base_dir = Path(base_dir).resolve()
        self.config = config
        
        # Generate Run ID
        self.run_id = f"SCADEX-{str(uuid.uuid4())[:8]}"
        
        # Setup output directories
        self.out_dir = Path(self.config.get("paths", "output_dir"))
        self._prepare_directories()
        
        # Initialize Core Managers
        self.logger = setup_logger(self.out_dir, self.config.get("pipeline", "debug_mode"))
        self.runtime = RuntimeManager(self.run_id, self.logger)
        self.artifact_mgr = ArtifactManager(self.base_dir)
        
    def _prepare_directories(self):
        """Ensures all output directories exist before execution."""
        dirs = [
            self.out_dir / "reports",
            self.out_dir / "figures",
            self.out_dir / "logs",
            self.out_dir / "benchmark",
            self.out_dir / "resilience",
            self.out_dir / "explanations",
            self.out_dir / "final_intelligence",
            self.base_dir / "data" / "intermediate",
            self.base_dir / "data" / "processed"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            
    def _export_artifacts(self):
        """Copies final processed outputs to the user-facing outputs/ directory."""
        self.runtime.start_stage("Artifact Export")
        try:
            processed_dir = self.base_dir / "data" / "processed"
            
            # Map of source to destination
            exports = {
                processed_dir / "scadex_final_intelligence.csv": self.out_dir / "final_intelligence" / "scadex_final_intelligence.csv",
                processed_dir / "resilience_intelligence.csv": self.out_dir / "resilience" / "resilience_intelligence.csv",
                processed_dir / "scadex_explanations.csv": self.out_dir / "explanations" / "scadex_explanations.csv",
                processed_dir / "scadex_benchmark.csv": self.out_dir / "benchmark" / "benchmark_summary.csv"
            }
            
            for src, dst in exports.items():
                if src.exists():
                    shutil.copy2(src, dst)
                    self.logger.info(f"Exported {src.name} to {dst.parent.name}/")
                else:
                    self.logger.warning(f"Expected output artifact missing for export: {src.name}")
                    
            self.runtime.complete_stage("Artifact Export")
        except Exception as e:
            self.runtime.fail_stage("Artifact Export", e)

    def execute(self):
        self.logger.info(f"🚀 Initializing SCADE-X Run: {self.run_id}")
        
        # Step 1: Input Validation
        self.runtime.start_stage("Input Validation")
        input_log = Path(self.config.get("paths", "input_log"))
        if not input_log.exists():
            self.logger.error(f"Critical input log missing: {input_log}")
            sys.exit(1)
        self.runtime.complete_stage("Input Validation")
        
        # Step 1.5: Environment Validation
        self.runtime.start_stage("Environment Validation")
        try:
            validate_environment(self.logger)
            self.runtime.complete_stage("Environment Validation")
        except Exception as e:
            fatal = self.runtime.fail_stage("Environment Validation", e)
            if fatal: sys.exit(1)
            
        # Step 2: ASTRA Subsystem
        if self.config.get("pipeline", "run_astra"):
            self.runtime.start_stage("ASTRA Execution")
            try:
                astra = ASTRARunner(self.runtime.ctx, self.artifact_mgr)
                success = astra.execute()
                if not success: raise RuntimeError("ASTRA execution failed internally.")
                self.runtime.complete_stage("ASTRA Execution")
            except Exception as e:
                fatal = self.runtime.fail_stage("ASTRA Execution", e)
                if fatal: sys.exit(1)

        # Step 3: SCADE Subsystem
        if self.config.get("pipeline", "run_scade"):
            self.runtime.start_stage("SCADE Execution")
            try:
                scade = SCADERunner(self.runtime.ctx, self.artifact_mgr)
                success = scade.execute()
                if not success: raise RuntimeError("SCADE execution failed internally.")
                self.runtime.complete_stage("SCADE Execution")
            except Exception as e:
                fatal = self.runtime.fail_stage("SCADE Execution", e)
                if fatal: sys.exit(1)
                
        # Step 4: Schema Normalization
        self.runtime.start_stage("Schema Normalization")
        try:
            normalizer = SchemaNormalizer(self.base_dir)
            normalizer.normalize()
            self.runtime.complete_stage("Schema Normalization")
        except Exception as e:
            fatal = self.runtime.fail_stage("Schema Normalization", e)
            if fatal: sys.exit(1)
            
        # Step 5: Resilience Intelligence
        self.runtime.start_stage("Resilience Intelligence")
        try:
            resilience = ResilienceEngine(self.base_dir)
            resilience.compute_resilience()
            self.runtime.complete_stage("Resilience Intelligence")
        except Exception as e:
            fatal = self.runtime.fail_stage("Resilience Intelligence", e)
            if fatal: sys.exit(1)
            
        # Step 6: Intelligence Fusion
        self.runtime.start_stage("Intelligence Fusion")
        try:
            fusion = IntelligenceFusionEngine(self.base_dir)
            fusion.execute_fusion()
            self.runtime.complete_stage("Intelligence Fusion")
        except Exception as e:
            fatal = self.runtime.fail_stage("Intelligence Fusion", e)
            if fatal: sys.exit(1)
            
        # Step 7: Explainability Layer
        self.runtime.start_stage("Explainability Generation")
        try:
            xai = XAIEngine(self.base_dir)
            xai.execute()
            self.runtime.complete_stage("Explainability Generation")
        except Exception as e:
            fatal = self.runtime.fail_stage("Explainability Generation", e)
            if fatal: sys.exit(1)
            
        # Step 8: Benchmarking Framework
        if self.config.get("pipeline", "run_benchmarks"):
            self.runtime.start_stage("Benchmarking")
            try:
                benchmark = SCADEXBenchmark(self.base_dir)
                benchmark.execute()
                self.runtime.complete_stage("Benchmarking")
            except Exception as e:
                # Benchmarking failures are non-fatal
                self.runtime.fail_stage("Benchmarking", e)
                
        # Step 9: Artifact Export
        self._export_artifacts()
        
        # Completion
        self.runtime.summarize()
        self.logger.info("✅ SCADE-X Pipeline Execution Completed Successfully.")
