from dataclasses import dataclass, field
from typing import Optional
from dataclass_wizard import JSONWizard
import logging
from logging.handlers import RotatingFileHandler
import os.path


@dataclass
class LoggingFormatConfig(JSONWizard):
    date: str
    output: str


@dataclass
class LoggingRotationConfig(JSONWizard):
    size: int
    backup: int


@dataclass
class LoggingConfig(JSONWizard):
    path: Optional[str] = None
    level: Optional[str] = None
    format: Optional[LoggingFormatConfig] = None
    rotation: Optional[LoggingRotationConfig] = None


@dataclass
class ModuleLoggingConfig(LoggingConfig):
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
    title: Optional[str]
    priority: Optional[int] = 3
    tags: list[str] = field(default_factory=str)


@dataclass
class Ntfy(JSONWizard):
    topic: str
    options: Optional[NtfyOptions] = None


@dataclass
class TopicConfig(JSONWizard):
    mqtt_topic: str
    ntfy: Ntfy


@dataclass
class NtfyModuleConfig(JSONWizard):
    logging: ModuleLoggingConfig
    configurations: list[TopicConfig] = field(default_factory=list)


@dataclass
class MQTTConfig(JSONWizard):
    enabled: Optional[bool] = False
    host: Optional[str] = "mqtt://localhost"


@dataclass
class DeviceConfig(JSONWizard):
    name: str
    mqtt: MQTTConfig


def __configure_logging(
    module_logging: ModuleLoggingConfig, root_logging: LoggingConfig
) -> None:
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
