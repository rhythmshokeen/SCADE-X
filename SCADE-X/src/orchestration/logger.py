"""
SCADE-X Logger
==============
Provides structured, centralized logging across all pipeline stages.
Generates persistent logs in outputs/logs/.
"""
import logging
from pathlib import Path
from datetime import datetime

def setup_logger(output_dir: Path, debug_mode: bool = False) -> logging.Logger:
    log_dir = Path(output_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"scadex_pipeline_{timestamp}.log"
    
    logger = logging.getLogger("SCADE-X")
    
    # Avoid adding handlers multiple times if instantiated repeatedly
    if not logger.handlers:
        level = logging.DEBUG if debug_mode else logging.INFO
        logger.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
        )
        
        # File Handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger
