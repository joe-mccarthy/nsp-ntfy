import paho.mqtt.client as mqtt
import json
from os.path import isfile
import logging
from .data.data_classes import (
    DeviceConfig,
    NtfyModuleConfig,
    LoggingConfig,
    __configure_logging,
    TopicConfig,
)
import requests

module_configuration: NtfyModuleConfig = None
nsp_configuration: DeviceConfig = None


def on_connect(client, userdata, flags, reason_code, properties):
    logging.info("connected to MQTT broker")


def on_message(client, userdata, msg):
    topic_config = get_configuration(msg.topic)
    if topic_config:
        logging.debug(f"found configuration for {msg.topic}")
        send_notification(msg, topic_config)
    else:
        logging.warn(f"no configuration found for topic {msg.topic}")


def send_notification(msg, config: TopicConfig) -> None:
    joiner = ","
    message = json.loads(str(msg.payload.decode("utf-8", "ignore")))["notification"]
    logging.debug(f"sending notification to ntfy {message}")
    requests.post(
        f"https://ntfy.sh/{config.ntfy.topic}",
        data=message,
        headers={
            "Title": f"{config.ntfy.options.title}",
            "Priority": f"{config.ntfy.options.priority}",
            "Tags": f"{joiner.join(config.ntfy.options.tags)}",
        },
    )
    logging.info("notification sent to ntfy")


def get_configuration(topic: str) -> TopicConfig:
    global module_configuration
    for configuration in module_configuration.configurations:
        if configuration.mqtt_topic == topic:
            return configuration
    return None

def __get_module_configuration(config_path:str) -> NtfyModuleConfig:
    if not isfile(config_path):
        msg = "Module Configuration file not found"
        logging.error(msg)
        raise IOError(msg)
    else:
        with open(config_path) as configuration_file:
            file_contents = configuration_file.read()
        return NtfyModuleConfig.from_dict(json.loads(file_contents))

def __get_nsp_configuration(config_path:str) -> (DeviceConfig,LoggingConfig):
    if not isfile(config_path):
        msg = "NSP Configuration file not found."
        logging.error(msg)
        raise IOError(msg)
    else:
        with open(config_path) as configuration_file:
            file_contents = configuration_file.read()
        nsp_logging = LoggingConfig.from_dict(json.loads(file_contents)["logging"])
        nsp_config = DeviceConfig.from_dict(json.loads(file_contents)["device"])
        return nsp_config, nsp_logging

def run(args) -> None:
    global module_configuration
    global nsp_configuration

    module_configuration = __get_module_configuration(args.configuration)
    nsp_configuration, logging_config = __get_nsp_configuration(args.nsp_configuration)
    __configure_logging(module_configuration.logging, logging_config)

    if nsp_configuration.mqtt.enabled:
        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.connect(nsp_configuration.mqtt.host)

        for configuration in module_configuration.configurations:
            mqttc.subscribe(configuration.mqtt_topic)

        mqttc.loop_forever()
    else:
        logging.error("MQTT on NSP not enabled in configuration, exiting NSP-NTFY.")
