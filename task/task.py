import time

from HLH.HLH_logfile import Logfile
from HLH.HLH_ocr import ParameterOCR as HLHOCR
from Printer.printer_log import PrinterLog
from Printer.printer_ocr import ParameterOCR as PrinterOCR
from MQTT.client import MQTTClient
import logging
import json

from Utils.config_util import load_config


class Task:
    def __init__(self, task_id, file_config_path, mqtt_config_path):
        # 发送mqtt消息
        self.client = MQTTClient(mqtt_config_path)
        self.mqtt_cfg = load_config(mqtt_config_path)

        # 根据task id进行初始化
        if task_id == 0:
            # 读取log file
            self.log_file = Logfile(file_config_path)
            # 识别屏幕参数
            self.param = HLHOCR(file_config_path)
            self.equipment_id = self.mqtt_cfg['equipment']['hlh']['id']
        elif task_id == 1:
            self.log_file = PrinterLog(file_config_path)
            self.param = PrinterOCR(file_config_path)
            self.equipment_id = self.mqtt_cfg['equipment']['printer']['id']
        self.client.setup()
        self.payload = {
            'log': [],
            'dynamic_param': {}
        }

    def exec_task(self):
        indent = self.mqtt_cfg['task']['out_indent']
        interval = self.mqtt_cfg['task']['interval']
        while True:
            self.__read_log()
            self.__get_parm()
            msg = json.dumps(self.payload, ensure_ascii=False, indent=indent)
            # print(msg)
            self.client.publish(self.client.topic_prefix + self.equipment_id, msg)
            time.sleep(interval)

    def __read_log(self):
        logging.info('Collecting Log...')
        self.log_file.read_log()
        self.payload['log'] = self.log_file.dump_dict()
        if self.payload['log'] and len(self.payload['log']) > 0:
            print(json.dumps(self.payload['log'][0], ensure_ascii=False, indent=2))
        else:
            logging.warning('No Log Files')

    def __get_parm(self):
        logging.info('Collecting Screen Parameters...')
        self.param.identify()
        self.payload['dynamic_param'] = self.param.dump_dict()
        print(json.dumps(self.payload['dynamic_param'], ensure_ascii=False, indent=2))
