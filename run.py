from HLH.HLH_logfile import Logfile
from HLH.HLH_ocr import ParameterOCR
from Utils.log_util import setup_logging
from Utils.config_util import load_config
from MQTT.client import MQTTClient

import os
import logging
import json
import time


def exec_task(equipment_id, log: Logfile, param_identify: ParameterOCR, mqtt_client: MQTTClient, interval=5):
    payload = {
        'log': None,
        'dynamic_param': None
    }
    while True:
        log.read_log()
        param_identify.identify()

        payload['log'] = log.dump_dict()
        payload['dynamic_param'] = param_identify.dump_dict()

        msg = json.dumps(payload, ensure_ascii=False, indent=2)
        logging.info(msg)
        mqtt_client.publish(client.topic_prefix + equipment_id, msg)
        time.sleep(interval)


if __name__ == '__main__':
    print('------program start------')
    cur_path = os.getcwd()
    print('current directory: ' + cur_path)
    hlh_config_path = "config/HLH_config.yaml"
    log_config_path = "config/log_config.yaml"
    mqtt_config_path = "config/mqtt_config.yaml"

    hlh_path = os.path.join(cur_path, hlh_config_path)
    log_path = os.path.join(cur_path, log_config_path)
    mqtt_path = os.path.join(cur_path, mqtt_config_path)

    # 配置logger
    setup_logging(log_path)

    # 读取log file
    log_file = Logfile(hlh_path)

    # 识别屏幕参数
    param = ParameterOCR(hlh_path)

    # 发送mqtt消息
    client = MQTTClient(mqtt_path)
    client.setup()

    mqtt_cfg = load_config(mqtt_path)
    interval = mqtt_cfg['task']['interval']
    exec_task(mqtt_cfg['equipment']['hlh']['id'], log_file, param, client, interval)
    # client.publish(topic='equipment/parameter/610', payload="asss")
