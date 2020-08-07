import os
import yaml


def load_config(path: str):
    """
    加载配置
    """
    cur_path = os.getcwd()
    yaml_path = os.path.join(cur_path, path)
    yaml_file = open(yaml_path, 'r', encoding='utf-8')
    cfg = yaml_file.read()
    yaml_file.close()
    return yaml.full_load(cfg)
