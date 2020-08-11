import os
import yaml
import logging


def load_config(path: str):
    """
    加载配置
    """
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.full_load(f)
    else:
        logging.error("No such file: %s", path)
        return None
