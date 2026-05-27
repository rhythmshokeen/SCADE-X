"""
SCADE-X Schema Normalizer
=========================
Loads ASTRA and SCADE subsystem artifacts, aligns mapping, handles
missing values gracefully, and produces the unified intelligence DataFrame.
"""
import pandas as pd
from pathlib import Path
from src.fusion.schema_registry import SchemaRegistry
import logging

logger = logging.getLogger("SCADE-X-Normalizer")

class SchemaNormalizer:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.astra_output = self.base_dir / "astra" / "data" / "processed" / "fused_risk_scores.csv"
        self.scade_output = self.base_dir / "scade" / "data" / "results.csv"
        self.output_path = self.base_dir / "data" / "intermediate" / "unified_case_intelligence.csv"
        
    def _load_astra(self) -> pd.DataFrame:
        if not self.astra_output.exists():
            logger.warning(f"ASTRA output missing at {self.astra_output}")
            return pd.DataFrame(columns=list(SchemaRegistry.get_astra_mappings().keys()))
        df = pd.read_csv(self.astra_output)
        return df.rename(columns=SchemaRegistry.get_astra_mappings())
        
    def _load_scade(self) -> pd.DataFrame:
        if not self.scade_output.exists():
            logger.warning(f"SCADE output missing at {self.scade_output}")
            return pd.DataFrame(columns=list(SchemaRegistry.get_scade_mappings().keys()))
        df = pd.read_csv(self.scade_output)
        return df.rename(columns=SchemaRegistry.get_scade_mappings())

    def normalize(self) -> pd.DataFrame:
        logger.info("Normalizing subsystem schemas into canonical form...")
        
        astra_df = self._load_astra()
        scade_df = self._load_scade()
        
        def _norm_id(x):
            sx = str(x)
            if sx.startswith('PO-'):
                return 'PO' + sx.split('-')[1].zfill(5)
            elif sx.startswith('PO') and len(sx) > 2:
                # Ensure 5 digits
                return 'PO' + sx[2:].zfill(5)
            return sx

        if not astra_df.empty:
            astra_df['case_id'] = astra_df['case_id'].apply(_norm_id)
        if not scade_df.empty:
            scade_df['case_id'] = scade_df['case_id'].apply(_norm_id)

        # Merge on case_id using an outer join to handle missing cases from either subsystem
        if not astra_df.empty and not scade_df.empty:
            unified = pd.merge(astra_df, scade_df, on="case_id", how="outer")
        elif not astra_df.empty:
            unified = astra_df
        elif not scade_df.empty:
            unified = scade_df
        else:
            logger.error("Both ASTRA and SCADE outputs are empty/missing.")
            return pd.DataFrame(columns=SchemaRegistry.get_canonical_columns())
            
        # Ensure all canonical columns exist (fill missing with NaNs/None)
        for col in SchemaRegistry.get_canonical_columns():
            if col not in unified.columns:
                unified[col] = None
                
        # Filter to only the canonical schema columns in definition order
        unified = unified[SchemaRegistry.get_canonical_columns()]
        
        # Basic normalization fixes (e.g. min-max scaling astra_risk_score if not 0-1)
        # Note: ASTRA risk score is an unbounded weighted sum in astra/src/fusion/fusion_engine.py
        # We scale it to 0-1 contextually if max > 1
        if "astra_risk_score" in unified.columns and unified["astra_risk_score"].notna().any():
            max_val = unified["astra_risk_score"].max()
            min_val = unified["astra_risk_score"].min()
            if max_val > 1.0 or min_val < 0.0:
                unified["astra_risk_score"] = (unified["astra_risk_score"] - min_val) / (max_val - min_val + 1e-9)

        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        unified.to_csv(self.output_path, index=False)
        logger.info(f"Unified intelligence matrix saved to {self.output_path}")
        return unified

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    normalizer = SchemaNormalizer(Path("."))
    normalizer.normalize()
