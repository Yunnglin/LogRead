import paho.mqtt.client as mqtt

from Utils.config_util import load_config


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


config = load_config('../config/mqtt_config.yaml')
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set('root', 'root1234')
client.connect(config['client']['ipaddr'], 16885, 600)  # 600为keepalive的时间间隔
client.subscribe('equipment/parameter/#', qos=0)
client.loop_forever()  # 保持连接
