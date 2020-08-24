import paho.mqtt.client as mqtt
import logging
from Utils.config_util import load_config


def on_connect(c, userdata, flags, rc):
    logging.info("Connected with result code: " + str(rc))


def on_message(c, userdata, msg):
    logging.info(msg.topic + " " + str(msg.payload))


def on_publish(c, userdata, mid):
    logging.info("Published message of Id: " + mid)


class MQTTClient:
    def __init__(self, path: str):
        self.config = load_config(path)['client']
        self.username = self.config['username']
        self.password = self.config['password']
        self.topic_prefix = self.config['topic_prefix']
        self.ipaddr = self.config['ipaddr']
        self.port = self.config['port']
        self.keep_alive = self.config['keepalive']
        self.client = mqtt.Client()

    def setup(self):
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_publish = on_publish
        self.client.username_pw_set(self.username, self.password)
        try:
            self.client.connect(host=self.ipaddr, port=self.port, keepalive=self.keep_alive)  # 600为keepalive的时间间隔
            self.client.loop_start()
        except TimeoutError:
            logging.error(f'连接失败 @ {self.ipaddr}:{self.port}', exc_info=True)
        except Exception:
            logging.error('网络连接错误', exc_info=True)

    def publish(self, topic, payload, qos=1):
        info = self.client.publish(topic=topic, payload=payload, qos=qos)
        try:
            if info.rc == mqtt.MQTT_ERR_SUCCESS:
                logging.info("Publish Success of message id:" + str(info.mid))
            elif info.rc == mqtt.MQTT_ERR_NO_CONN:
                logging.info("No Connection!")
            elif info.rc == mqtt.MQTT_ERR_QUEUE_SIZE:
                logging.info("Queue size Error!")
        except ValueError:
            logging.error("Error in publish", exc_info=True)
