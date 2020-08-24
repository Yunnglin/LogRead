from MQTT.client import MQTTClient
from Utils.img_util import base64_to_image
from Utils.log_util import setup_logging
from Utils.config_util import load_config
from HLH.HLH_ocr import ParameterOCR as HLHOCR
from Printer.printer_ocr import ParameterOCR as PrinterOCR
from flask import Flask, request
import os
import logging
import json

app = Flask(__name__)


@app.route('/')
def hello():
    return 'hello'


@app.route('/equipment/<e_id>', methods=['POST'])
def process_data(e_id):
    _json = json.loads(request.json)
    payload = {'log': _json.get('log'), 'dynamic_param': {}}
    raw_img = _json.get('image')
    ocr = None
    if e_id == mqtt_cfg['equipment']['hlh']['id']:
        ocr = HLHOCR(hlh_path)
    elif e_id == mqtt_cfg['equipment']['printer']['id']:
        ocr = PrinterOCR(printer_path)
    # 将接收到的base64的图像再转为图像
    ocr.image = base64_to_image(raw_img)
    ocr.identify()
    payload['dynamic_param'] = ocr.dump_dict()

    msg = json.dumps(payload, ensure_ascii=False, indent=None)
    client.publish(client.topic_prefix + e_id, msg)
    if mqtt_cfg['task']['show_info']:
        print(json.dumps(payload['dynamic_param'], ensure_ascii=False, indent=None))
    return ""


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

    client = MQTTClient(mqtt_config_path)
    client.setup()

    app.run(host='0.0.0.0', port=5000, debug=False)
