from Utils.log_util import setup_logging
from Utils.config_util import load_config
from task import Task

import os
import logging
import json

if __name__ == '__main__':
    print('------program start------')
    cur_path = os.getcwd()

    hlh_config_path = "config/HLH_config.yaml"
    log_config_path = "config/log_config.yaml"
    mqtt_config_path = "config/mqtt_config.yaml"
    printer_config_path = "config/printer_config.yaml"

    hlh_path = os.path.join(cur_path, hlh_config_path)
    log_path = os.path.join(cur_path, log_config_path)
    mqtt_path = os.path.join(cur_path, mqtt_config_path)
    printer_path = os.path.join(cur_path, printer_config_path)

    # 配置logger
    setup_logging(log_path)
    logging.info('current directory: ' + cur_path)

    # 配置任务
    mqtt_cfg = load_config(mqtt_path)
    logging.info('Loading Task Configuration：' + json.dumps(load_config(mqtt_path), indent=2))
    task_id = mqtt_cfg['task']['identifier']
    if task_id == 0:
        # 在回流焊上运行
        logging.info('Executing on Reflow Soldering Machine')
        executor = Task(task_id, hlh_path, mqtt_path)
        executor.exec_task()
    elif task_id == 1:
        # 在回流焊上运行
        logging.info('Executing on Printer')
        executor = Task(task_id, printer_path, mqtt_path)
        executor.exec_task()
