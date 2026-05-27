from pathlib import Path
import yaml


def load_config(config_path="configs/app_config.yaml"):
    """
    Load ASTRA YAML configuration file.
    """

    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}"
        )

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    return config
