from utils.config_loader import load_config
from utils.logger import setup_logger


def main():

    logger = setup_logger()

    logger.info("Starting ASTRA...")

    config = load_config()

    logger.info(
        f"Project: {config['project']['name']}"
    )

    logger.info(
        f"Version: {config['project']['version']}"
    )

    logger.info(
        f"Environment: "
        f"{config['project']['environment']}"
    )

    logger.info("ASTRA boot successful")


if __name__ == "__main__":
    main()
