import logging
from pathlib import Path


def setup_logger():

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(
                log_dir / "astra.log"
            ),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("ASTRA")
