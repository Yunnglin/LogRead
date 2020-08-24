import time
from HLH.HLH_logfile import Logfile
from Printer.printer_log import PrinterLog
from PIL import ImageGrab,Image
import logging
import json
from requests import post

from Utils.config_util import load_config
from Utils.img_util import image_to_base64


class SingleTask:
    def __init__(self, task_id, file_config_path, mqtt_config_path):
        # 发送mqtt消息
        self.mqtt_cfg = load_config(mqtt_config_path)
        # 根据task id进行初始化
        if task_id == 0:
            # 读取log file
            self.log_file = Logfile(file_config_path)
            self.equipment_id = self.mqtt_cfg['equipment']['hlh']['id']
        elif task_id == 1:
            self.log_file = PrinterLog(file_config_path)
            self.equipment_id = self.mqtt_cfg['equipment']['printer']['id']
        self.payload = {
            'log': [],
            'image': {}
        }

    def exec_task(self):
        indent = self.mqtt_cfg['task']['out_indent']
        interval = self.mqtt_cfg['task']['interval']
        while True:
            self.__read_log()
            self.__get_screen()
            msg = json.dumps(self.payload, ensure_ascii=False, indent=indent)
            # 发送屏幕截图和解析好的日志到外围机器
            try:
                self.request(msg)
            except Exception:
                logging.exception("连接服务器出错!!!")
            time.sleep(interval)

    def __read_log(self):
        logging.info('Collecting Log...')
        self.log_file.read_log()
        self.payload['log'] = self.log_file.dump_dict()
        if self.payload['log'] and len(self.payload['log']) > 0:
            print(json.dumps(self.payload['log'][0], ensure_ascii=False, indent=2))
        else:
            logging.warning('No Log Files')

    def __get_screen(self):
        logging.info('Collecting Screen image...')
        image = ImageGrab.grab((0, 0,
                                self.mqtt_cfg['task']['screen_size'][0],
                                self.mqtt_cfg['task']['screen_size'][1]))
        # image = Image.open("./OCRTest/resource/printer.png")
        try:
            self.payload['image'] = image_to_base64(image)
        except Exception:
            logging.exception('Error in collecting screen')

    def request(self, msg):
        ip = self.mqtt_cfg['equipment']['outer_pc']['ipaddr']
        url = 'http://' + ip + '/equipment/' + self.equipment_id

        post(url=url, json=msg)
