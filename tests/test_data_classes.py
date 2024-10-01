import pytest

from app.data.data_classes import (
    ModuleLoggingConfig,
    LoggingConfig,
    LoggingFormatConfig,
    LoggingRotationConfig,
)


@pytest.fixture
def module_logging_config():
    return ModuleLoggingConfig(
        path="/tmp/logs",
        level="DEBUG",
        format=LoggingFormatConfig(date="%Y-%m-%d %H:%M:%S", output="%(message)s"),
        rotation=LoggingRotationConfig(size=1024, backup=3),
        file="test.log",
    )


@pytest.fixture
def root_logging_config():
    return LoggingConfig(
        path="/tmp/logs",
        level="INFO",
        format=LoggingFormatConfig(date="%Y-%m-%d %H:%M:%S", output="%(message)s"),
        rotation=LoggingRotationConfig(size=2048, backup=5),
    )


def test_merge_logging_config(module_logging_config, root_logging_config):
    module_logging_config.path = None
    module_logging_config.level = None
    module_logging_config.format = None
    module_logging_config.rotation = None

    module_logging_config.merge(root_logging_config)

    assert module_logging_config.path == root_logging_config.path
    assert module_logging_config.level == root_logging_config.level
    assert module_logging_config.format == root_logging_config.format
    assert module_logging_config.rotation == root_logging_config.rotation


def test_merge_logging_config_partial(module_logging_config, root_logging_config):
    module_logging_config.path = None
    module_logging_config.level = "DEBUG"
    module_logging_config.format = None
    module_logging_config.rotation = LoggingRotationConfig(size=512, backup=1)

    module_logging_config.merge(root_logging_config)

    assert module_logging_config.path == root_logging_config.path
    assert module_logging_config.level == "DEBUG"
    assert module_logging_config.format == root_logging_config.format
    assert module_logging_config.rotation.size == 512
    assert module_logging_config.rotation.backup == 1
