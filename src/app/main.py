import paho.mqtt.client as mqtt
import json
from os.path import isfile
from typing import Tuple
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
    """
    Callback function that is called when the client connects to the MQTT broker.

    Args:
        client: The MQTT client instance.
        userdata: The private user data as set in the MQTT client constructor.
        flags: Response flags sent by the broker.
        reason_code: The connection result.
        properties: The MQTT properties returned by the broker.

    Returns:
        None
    """
    logging.info("connected to MQTT broker")


def on_message(client, userdata, msg):
    """
    Callback function that is called when a message is received.

    Args:
        client: The MQTT client instance that received the message.
        userdata: The private user data as set in the MQTT client constructor.
        msg: The received message.

    Returns:
        None

    Raises:
        None
    """
    topic_config = get_configuration(msg.topic)
    if topic_config:
        logging.debug(f"found configuration for {msg.topic}")
        send_notification(msg, topic_config)
    else:
        logging.warn(f"no configuration found for topic {msg.topic}")


def send_notification(msg, config: TopicConfig) -> None:
    """
    Sends a notification to the ntfy service.

    Args:
        msg: The message to be sent as a notification.
        config: The configuration for the ntfy service.

    Returns:
        None
    """
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
    """
    Retrieves the configuration for a given MQTT topic.

    Args:
        topic (str): The MQTT topic to retrieve the configuration for.

    Returns:
        TopicConfig: The configuration object for the given topic, or None if no configuration is found.
    """
    global module_configuration
    for configuration in module_configuration.configurations:
        if configuration.mqtt_topic == topic:
            return configuration
    return None


def __get_module_configuration(config_path: str) -> NtfyModuleConfig:
    """
    Retrieves the module configuration from the specified file path.

    Args:
        config_path (str): The path to the module configuration file.

    Returns:
        NtfyModuleConfig: The module configuration object.

    Raises:
        IOError: If the module configuration file is not found.
    """
    if not isfile(config_path):
        msg = "Module Configuration file not found"
        logging.error(msg)
        raise IOError(msg)
    else:
        with open(config_path) as configuration_file:
            file_contents = configuration_file.read()
        return NtfyModuleConfig.from_dict(json.loads(file_contents))


def __get_nsp_configuration(config_path: str) -> Tuple[DeviceConfig, LoggingConfig]:
    """
    Retrieves the NSP configuration from the specified file path.

    Args:
        config_path (str): The path to the NSP configuration file.

    Returns:
        Tuple[DeviceConfig, LoggingConfig]: A tuple containing the NSP device configuration and logging configuration.

    Raises:
        IOError: If the NSP configuration file is not found.
    """
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
    """
    Runs the main function of the NSP-NTFY application.

    Args:
        args: The command line arguments.

    Returns:
        None
    """

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
