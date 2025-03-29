import unittest
import pytest
from unittest.mock import patch, MagicMock
from nsp_ntfy.app.data.data_classes import (
    TopicConfig,
    Ntfy,
    NtfyModuleConfig,
    LoggingConfig,
)
from nsp_ntfy.app.main import (
    get_configuration,
    send_notification,
    on_connect,
    on_message,
    __get_module_configuration,
    __get_nsp_configuration,
    DeviceConfig,
    run,
)


@patch("nsp_ntfy.app.main.module_configuration", autospec=True)
def test_get_configuration_found(mock_module_configuration):
    # Arrange
    topic = "test/topic"
    expected_config = TopicConfig(mqtt_topic=topic, ntfy=Ntfy(topic=topic))
    mock_module_configuration.configurations = [expected_config]

    # Act
    result = get_configuration(topic)

    # Assert
    assert result == expected_config


@patch("nsp_ntfy.app.main.module_configuration", autospec=True)
def test_get_configuration_not_found(mock_module_configuration):
    # Arrange
    topic = "test/topic"
    mock_module_configuration.configurations = [
        TopicConfig(mqtt_topic="other/topic", ntfy=Ntfy(topic="other/topic"))
    ]

    # Act
    result = get_configuration(topic)

    # Assert
    assert result is None


@patch("nsp_ntfy.app.main.module_configuration", autospec=True)
def test_get_configuration_empty_configurations(mock_module_configuration):
    # Arrange
    topic = "test/topic"
    mock_module_configuration.configurations = []

    # Act
    result = get_configuration(topic)

    assert result is None


@patch("nsp_ntfy.app.main.module_configuration", autospec=True)
def test_get_configuration_found_second(mock_module_configuration):
    # Arrange
    topic = "test/topic"
    expected_config = TopicConfig(mqtt_topic=topic, ntfy=Ntfy(topic=topic))
    mock_module_configuration.configurations = [expected_config]

    # Act
    result = get_configuration(topic)

    # Assert
    assert result == expected_config


@patch("nsp_ntfy.app.main.module_configuration", autospec=True)
def test_get_configuration_not_found_third(mock_module_configuration):
    # Arrange
    topic = "test/topic"
    mock_module_configuration.configurations = [
        TopicConfig(mqtt_topic="other/topic", ntfy=Ntfy(topic="other/topic"))
    ]

    # Act
    result = get_configuration(topic)

    # Assert
    assert result is None


@patch("nsp_ntfy.app.main.module_configuration", autospec=True)
def test_get_configuration_empty_configurations_second(mock_module_configuration):
    # Arrange
    topic = "test/topic"
    mock_module_configuration.configurations = []

    # Act
    result = get_configuration(topic)

    assert result is None


@patch("nsp_ntfy.app.main.logging")
def test_on_connect(mock_logging):
    # Arrange
    client = MagicMock()
    userdata = MagicMock()
    flags = MagicMock()
    reason_code = MagicMock()
    properties = MagicMock()

    # Act
    on_connect(client, userdata, flags, reason_code, properties)

    # Assert
    mock_logging.info.assert_called_once_with("connected to MQTT broker")


@patch("nsp_ntfy.app.main.get_configuration")
@patch("nsp_ntfy.app.main.send_notification")
@patch("nsp_ntfy.app.main.logging")
def test_on_message_with_configuration(
    mock_logging, mock_send_notification, mock_get_configuration
):
    # Arrange
    client = MagicMock()
    userdata = MagicMock()
    msg = MagicMock()
    msg.topic = "test/topic"
    msg.payload = b'{"notification": "test message"}'
    topic_config = MagicMock()
    mock_get_configuration.return_value = topic_config

    # Act
    on_message(client, userdata, msg)

    # Assert
    mock_get_configuration.assert_called_once_with("test/topic")
    mock_logging.debug.assert_called_once_with("found configuration for test/topic")
    mock_send_notification.assert_called_once_with(msg, topic_config)


@patch("nsp_ntfy.app.main.get_configuration")
@patch("nsp_ntfy.app.main.logging")
def test_on_message_without_configuration(mock_logging, mock_get_configuration):
    # Arrange
    client = MagicMock()
    userdata = MagicMock()
    msg = MagicMock()
    msg.topic = "test/topic"
    mock_get_configuration.return_value = None

    # Act
    on_message(client, userdata, msg)

    # Assert
    mock_get_configuration.assert_called_once_with("test/topic")
    mock_logging.warn.assert_called_once_with(
        "no configuration found for topic test/topic"
    )


@patch("nsp_ntfy.app.main.requests.post")
@patch("nsp_ntfy.app.main.logging")
def test_send_notification(mock_logging, mock_requests_post):
    # Arrange
    msg = MagicMock()
    msg.payload = b'{"notification": "test message"}'
    config = MagicMock()
    config.ntfy.topic = "test_topic"
    config.ntfy.options.title = "Test Title"
    config.ntfy.options.priority = "high"
    config.ntfy.options.tags = ["tag1", "tag2"]

    # Act
    send_notification(msg, config)

    # Assert
    mock_logging.debug.assert_called_once_with(
        "sending notification to ntfy test message"
    )
    mock_requests_post.assert_called_once_with(
        "https://ntfy.sh/test_topic",
        data="test message",
        headers={
            "Title": "Test Title",
            "Priority": "high",
            "Tags": "tag1,tag2",
        },
    )
    mock_logging.info.assert_called_once_with("notification sent to ntfy")


@patch("nsp_ntfy.app.main.isfile")
@patch("nsp_ntfy.app.main.logging")
def test_get_module_configuration_file_not_found(mock_logging, mock_isfile):
    # Arrange
    config_path = "invalid/path/to/config.json"
    mock_isfile.return_value = False

    # Act & Assert
    with pytest.raises(IOError, match="Module Configuration file not found"):
        __get_module_configuration(config_path)
    mock_logging.error.assert_called_once_with("Module Configuration file not found")


@patch("nsp_ntfy.app.main.isfile")
@patch(
    "nsp_ntfy.app.main.open",
    new_callable=unittest.mock.mock_open,
    read_data='{"configurations": []}',
)
@patch("nsp_ntfy.app.main.NtfyModuleConfig.from_dict")
def test_get_module_configuration_success(mock_from_dict, mock_open, mock_isfile):
    # Arrange
    config_path = "valid/path/to/config.json"
    mock_isfile.return_value = True
    expected_config = NtfyModuleConfig(logging=LoggingConfig(), configurations=[])
    mock_from_dict.return_value = expected_config

    # Act
    result = __get_module_configuration(config_path)

    # Assert
    mock_isfile.assert_called_once_with(config_path)
    mock_open.assert_called_once_with(config_path)
    mock_from_dict.assert_called_once_with({"configurations": []})
    assert result == expected_config


@patch("nsp_ntfy.app.main.isfile")
@patch("nsp_ntfy.app.main.logging")
def test_get_nsp_configuration_file_not_found(mock_logging, mock_isfile):
    # Arrange
    config_path = "invalid/path/to/config.json"
    mock_isfile.return_value = False

    # Act & Assert
    with pytest.raises(IOError, match="NSP Configuration file not found."):
        __get_nsp_configuration(config_path)
    mock_logging.error.assert_called_once_with("NSP Configuration file not found.")


@patch("nsp_ntfy.app.main.isfile")
@patch(
    "nsp_ntfy.app.main.open",
    new_callable=unittest.mock.mock_open,
    read_data='{"logging": {}, "device": {}}',
)
@patch("nsp_ntfy.app.main.LoggingConfig.from_dict")
@patch("nsp_ntfy.app.main.DeviceConfig.from_dict")
def test_get_nsp_configuration_success(
    mock_device_from_dict, mock_logging_from_dict, mock_open, mock_isfile
):
    # Arrange
    config_path = "valid/path/to/config.json"
    mock_isfile.return_value = True
    expected_logging_config = LoggingConfig()
    expected_device_config = DeviceConfig(
        name="test", mqtt={"enabled": False, "host": "mqtt://localhost"}
    )
    mock_logging_from_dict.return_value = expected_logging_config
    mock_device_from_dict.return_value = expected_device_config

    # Act
    result = __get_nsp_configuration(config_path)

    # Assert
    mock_isfile.assert_called_once_with(config_path)
    mock_open.assert_called_once_with(config_path)
    mock_logging_from_dict.assert_called_once_with({})
    mock_device_from_dict.assert_called_once_with({})
    assert result == (expected_device_config, expected_logging_config)


@patch("nsp_ntfy.app.main.isfile")
@patch("nsp_ntfy.app.main.logging")
def test_get_nsp_configuration_file_not_found_log(mock_logging, mock_isfile):
    # Arrange
    config_path = "invalid/path/to/config.json"
    mock_isfile.return_value = False

    # Act & Assert
    with pytest.raises(IOError, match="NSP Configuration file not found."):
        __get_nsp_configuration(config_path)
    mock_logging.error.assert_called_once_with("NSP Configuration file not found.")


@patch("nsp_ntfy.app.main.isfile")
@patch(
    "nsp_ntfy.app.main.open",
    new_callable=unittest.mock.mock_open,
    read_data='{"logging": {}, "device": {}}',
)
@patch("nsp_ntfy.app.main.LoggingConfig.from_dict")
@patch("nsp_ntfy.app.main.DeviceConfig.from_dict")
def test_get_nsp_configuration_success_merge(
    mock_device_from_dict, mock_logging_from_dict, mock_open, mock_isfile
):
    # Arrange
    config_path = "valid/path/to/config.json"
    mock_isfile.return_value = True
    expected_logging_config = LoggingConfig()
    expected_device_config = DeviceConfig(
        name="test", mqtt={"enabled": False, "host": "mqtt://localhost"}
    )
    mock_logging_from_dict.return_value = expected_logging_config
    mock_device_from_dict.return_value = expected_device_config

    # Act
    result = __get_nsp_configuration(config_path)

    # Assert
    mock_isfile.assert_called_once_with(config_path)
    mock_open.assert_called_once_with(config_path)
    mock_logging_from_dict.assert_called_once_with({})
    mock_device_from_dict.assert_called_once_with({})
    assert result == (expected_device_config, expected_logging_config)


@patch("nsp_ntfy.app.main.__get_module_configuration")
@patch("nsp_ntfy.app.main.__get_nsp_configuration")
@patch("nsp_ntfy.app.main.__configure_logging")
@patch("nsp_ntfy.app.main.mqtt.Client")
@patch("nsp_ntfy.app.main.logging")
def test_run_mqtt_enabled(
    mock_logging,
    mock_mqtt_client,
    mock_configure_logging,
    mock_get_nsp_configuration,
    mock_get_module_configuration,
):
    # Arrange
    args = MagicMock()
    args.configuration = "path/to/module/config.json"
    args.nsp_configuration = "path/to/nsp/config.json"

    mock_module_config = MagicMock()
    mock_module_config.logging = MagicMock()
    mock_module_config.configurations = [
        TopicConfig(mqtt_topic="test/topic", ntfy=Ntfy(topic="test_topic"))
    ]
    mock_get_module_configuration.return_value = mock_module_config

    mock_nsp_config = MagicMock()
    mock_nsp_config.mqtt.enabled = True
    mock_nsp_config.mqtt.host = "mqtt://localhost"
    mock_logging_config = MagicMock()
    mock_get_nsp_configuration.return_value = (mock_nsp_config, mock_logging_config)

    mock_mqtt_instance = MagicMock()
    mock_mqtt_client.return_value = mock_mqtt_instance

    # Act
    run(args)

    # Assert
    mock_get_module_configuration.assert_called_once_with(args.configuration)
    mock_get_nsp_configuration.assert_called_once_with(args.nsp_configuration)
    mock_configure_logging.assert_called_once_with(
        mock_module_config.logging, mock_logging_config
    )
    mock_mqtt_instance.on_connect = on_connect
    mock_mqtt_instance.on_message = on_message
    mock_mqtt_instance.connect.assert_called_once_with("mqtt://localhost")
    mock_mqtt_instance.subscribe.assert_called_once_with("test/topic")
    mock_mqtt_instance.loop_forever.assert_called_once()


@patch("nsp_ntfy.app.main.__get_module_configuration")
@patch("nsp_ntfy.app.main.__get_nsp_configuration")
@patch("nsp_ntfy.app.main.__configure_logging")
@patch("nsp_ntfy.app.main.mqtt.Client")
@patch("nsp_ntfy.app.main.logging")
def test_run_mqtt_disabled(
    mock_logging,
    mock_mqtt_client,
    mock_configure_logging,
    mock_get_nsp_configuration,
    mock_get_module_configuration,
):
    # Arrange
    args = MagicMock()
    args.configuration = "path/to/module/config.json"
    args.nsp_configuration = "path/to/nsp/config.json"

    mock_module_config = MagicMock()
    mock_module_config.logging = MagicMock()
    mock_get_module_configuration.return_value = mock_module_config

    mock_nsp_config = MagicMock()
    mock_nsp_config.mqtt.enabled = False
    mock_logging_config = MagicMock()
    mock_get_nsp_configuration.return_value = (mock_nsp_config, mock_logging_config)

    # Act
    run(args)

    # Assert
    mock_get_module_configuration.assert_called_once_with(args.configuration)
    mock_get_nsp_configuration.assert_called_once_with(args.nsp_configuration)
    mock_configure_logging.assert_called_once_with(
        mock_module_config.logging, mock_logging_config
    )
    mock_logging.error.assert_called_once_with(
        "MQTT on NSP not enabled in configuration, exiting NSP-NTFY."
    )
    mock_mqtt_client.assert_not_called()
