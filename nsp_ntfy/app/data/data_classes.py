from dataclasses import dataclass, field
from typing import List, Optional
from dataclass_wizard import JSONWizard
import logging
from logging.handlers import RotatingFileHandler
import os.path


@dataclass
class LoggingFormatConfig(JSONWizard):
    """
    Represents the configuration for logging format.

    Attributes:
        date (str): The date format for logging.
        output (str): The output format for logging.
    """

    date: str
    output: str


@dataclass
class LoggingRotationConfig(JSONWizard):
    """
    Represents the configuration for logging rotation.

    Attributes:
        size (int): The maximum size (in bytes) of the log file before rotation.
        backup (int): The number of backup log files to keep.
    """

    size: int
    backup: int


@dataclass
class LoggingConfig(JSONWizard):
    """
    Represents the configuration for logging.

    Attributes:
        path (Optional[str]): The path to the log file.
        level (Optional[str]): The logging level.
        format (Optional[LoggingFormatConfig]): The logging format configuration.
        rotation (Optional[LoggingRotationConfig]): The logging rotation configuration.
    """

    path: Optional[str] = None
    level: Optional[str] = None
    format: Optional[LoggingFormatConfig] = None
    rotation: Optional[LoggingRotationConfig] = None


@dataclass
class ModuleLoggingConfig(LoggingConfig):
    """
    Configuration class for module-specific logging settings.

    Attributes:
        file (Optional[str]): The file path for the log file. Defaults to None.
    """

    """
        Merge the given logging configuration with the current configuration.

        Args:
            logging_config (LoggingConfig): The logging configuration to merge.

        Returns:
            None
    """

    file: Optional[str] = None

    def merge(self, logging_config: LoggingConfig):
        if not self.path:
            self.path = logging_config.path
        if not self.level:
            self.level = logging_config.level
        if not self.format:
            self.format = logging_config.format
        if not self.rotation:
            self.rotation = logging_config.rotation


@dataclass
class NtfyOptions(JSONWizard):
    """
    Represents the options for a notification.

    Attributes:
        title (Optional[str]): The title of the notification.
        priority (Optional[int]): The priority of the notification. Defaults to 3.
        tags (List[str]): The tags associated with the notification. Defaults to an empty list.
    """

    title: Optional[str]
    priority: Optional[int] = 3
    tags: List[str] = field(default_factory=list)


@dataclass
class Ntfy(JSONWizard):
    """
    Represents a notification object.

    Attributes:
        topic (str): The topic of the notification.
        options (Optional[NtfyOptions]): The options for the notification. Defaults to None.
    """

    topic: str
    options: Optional[NtfyOptions] = None


@dataclass
class TopicConfig(JSONWizard):
    """
    Represents the configuration for a topic.

    Attributes:
        mqtt_topic (str): The MQTT topic.
        ntfy (Ntfy): The notification configuration.
    """

    mqtt_topic: str
    ntfy: Ntfy


@dataclass
class NtfyModuleConfig(JSONWizard):
    class NtfyModuleConfig:
        """
        Represents the configuration for an Ntfy module.

        Attributes:
            logging (ModuleLoggingConfig): The logging configuration for the module.
            configurations (list[TopicConfig]): The list of topic configurations for the module.
        """

    logging: ModuleLoggingConfig
    configurations: List[TopicConfig] = field(default_factory=list)


@dataclass
class MQTTConfig(JSONWizard):
    """
    Represents the MQTT configuration.

    Attributes:
        enabled (Optional[bool]): Whether MQTT is enabled. Defaults to False.
        host (Optional[str]): The MQTT host. Defaults to "mqtt://localhost".
    """

    enabled: Optional[bool] = False
    host: Optional[str] = "mqtt://localhost"


@dataclass
class DeviceConfig(JSONWizard):
    """
    Represents the configuration for a device.

    Attributes:
        name (str): The name of the device.
        mqtt (MQTTConfig): The MQTT configuration for the device.
    """

    name: str
    mqtt: MQTTConfig


def __configure_logging(
    module_logging: ModuleLoggingConfig, root_logging: LoggingConfig
) -> None:
    """
    Configures logging based on the provided module_logging and root_logging configurations.
    Args:
        module_logging (ModuleLoggingConfig): The configuration for module-specific logging.
        root_logging (LoggingConfig): The root logging configuration.
    Returns:
        None
    """

    module_logging.merge(root_logging)
    log_conf = module_logging

    if not os.path.exists(log_conf.path):
        os.makedirs(log_conf.path)

    file = f"{log_conf.path}/{log_conf.file}"
    handler = RotatingFileHandler(
        file, maxBytes=log_conf.rotation.size, backupCount=log_conf.rotation.backup
    )

    logging.basicConfig(
        level=log_conf.level,
        format=log_conf.format.output,
        datefmt=log_conf.format.date,
        handlers=[handler],
    )

    logging.info("configuration created")
