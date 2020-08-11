import logging.config
import os
from Utils.config_util import load_config


def setup_logging(default_path="log_config.yaml", default_level=logging.INFO, env_key="LOG_CFG"):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    config = load_config(path)
    if config:
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

