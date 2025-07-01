# NSP Ntfy

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/joe-mccarthy/nsp-ntfy/build-and-test.yml?style=for-the-badge)
![Coveralls](https://img.shields.io/coverallsCoverage/github/joe-mccarthy/nsp-ntfy?style=for-the-badge)
![Sonar Quality Gate](https://img.shields.io/sonar/quality_gate/joe-mccarthy_nsp-ntfy?server=https%3A%2F%2Fsonarcloud.io&style=for-the-badge)
![PyPI - Version](https://img.shields.io/pypi/v/nsp-ntfy?style=for-the-badge)
[![GitHub License](https://img.shields.io/github/license/joe-mccarthy/nsp-ntfy?cacheSeconds=1&style=for-the-badge)](LICENSE)

## Overview

NSP-NTFY is a bridge between Night Sky Pi's MQTT messages and [ntfy.sh](https://ntfy.sh) push notifications. When Night Sky Pi detects events (like satellite passes or ISS visibility), it can publish these to a local MQTT broker. NSP-NTFY subscribes to these events and forwards them as push notifications to your devices via ntfy.sh, allowing you to receive real-time astronomy alerts without exposing your local network.

## Table of Contents

- [Prerequisites](#prerequisites)
  - [Python](#python)
  - [MQTT Broker](#mqtt-broker)
- [Installation](#installation)
- [Configuration](#configuration)
  - [NSP Configuration](#nsp-configuration)
  - [NSP-NTFY Configuration](#nsp-ntfy-configuration)
- [Usage](#usage)
  - [Running as a Service](#running-as-a-service)
  - [Manual Execution](#manual-execution)
- [Notification Examples](#notification-examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before deploying NSP-NTFY, ensure you have the following prerequisites configured:

### Python

NSP-NTFY is written in Python and has been tested with the following Python versions:

- Python 3.12

### MQTT Broker

Night Sky Pi has the ability to publish events to an MQTT broker. The intent of this is so that other modules can react to the events to complete additional actions. Initially this broker will only run locally therefore only allow clients that reside on the same device as intended. Firstly we need to install MQTT on the Raspberry Pi.

```bash
sudo apt update && sudo apt upgrade
sudo apt install -y mosquitto
sudo apt install -y mosquitto-clients # Optional for testing locally
sudo systemctl enable mosquitto.service
sudo reboot # Just something I like to do, this is optional as well
```

## Installation

Installing NSP-NTFY is straightforward using pip:

```bash
# Install from PyPI
pip install nsp-ntfy

# Or install development version directly from GitHub
pip install git+https://github.com/joe-mccarthy/nsp-ntfy.git
```

## Configuration

### NSP Configuration

First, ensure your Night Sky Pi is configured to publish MQTT messages. These settings are in the Night Sky Pi configuration file:

```json
"device" : {
    "mqtt" : {
        "enabled": true,
        "host": "127.0.0.1"
    }
}
```

### NSP-NTFY Configuration

Create a configuration file for NSP-NTFY (`nsp-ntfy-config.json`):

```json
{
  "mqtt": {
    "broker": "127.0.0.1",
    "port": 1883,
    "username": "",
    "password": "",
    "topic": "nsp/notifications/#"
  },
  "ntfy": {
    "server": "https://ntfy.sh",
    "topic": "your-unique-topic-name",
    "priority": "default",
    "tags": ["satellite", "astronomy"]
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/nsp-ntfy.log"
  }
}
```

Configuration options explained:

- **MQTT Settings**:
  - `broker`: Address of your MQTT broker (default: 127.0.0.1)
  - `port`: MQTT broker port (default: 1883)
  - `username` & `password`: Credentials if your broker requires authentication
  - `topic`: MQTT topic pattern to subscribe to (default: "nsp/notifications/#")

- **NTFY Settings**:
  - `server`: NTFY server URL (default: https://ntfy.sh)
  - `topic`: Your unique notification topic - keep this private as anyone with this name can send/receive notifications
  - `priority`: Default notification priority (default, min, low, high, urgent)
  - `tags`: Default tags to include with notifications

- **Logging Settings**:
  - `level`: Logging level (DEBUG, INFO, WARNING, ERROR)
  - `file`: Log file path

## Usage

### Running as a Service

It's recommended that NSP-NTFY is run as a service. This ensures that it doesn't stop if a user logs off and continues running after system restarts.

```bash
sudo nano /etc/systemd/system/nsp-ntfy.service
```

Next step is to update the service definition to the correct paths and running as the correct user:

```bash
[Unit]
Description=nsp-ntfy
After=network.target

[Service]
Type=Simple
# update this to be your current user
User=username 
# the location of the nsp-ntfy to work within
WorkingDirectory=/home/username/
# update these paths to be the location of the nsp-ntfy.sh 
# update argument to where you previously copied the json configuration.
ExecStart=nsp-ntfy /home/username/nsp-ntfy-config.json /home/username/nsp-config.json 
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Next is to enable and start the service.

```bash
sudo systemctl daemon-reload
sudo systemctl start nsp-ntfy
sudo systemctl enable nsp-ntfy
```

### Manual Execution

To run NSP-NTFY manually, execute the following command:

```bash
nsp-ntfy /path/to/nsp-ntfy-config.json /path/to/nsp-config.json
```

## Notification Examples

Here are some examples of notifications you might receive:

- **Satellite Pass**: "Satellite XYZ will be visible at 10:15 PM for 5 minutes."
- **ISS Visibility**: "The ISS will be visible at 9:30 PM for 6 minutes."
- **Astronomy Alert**: "Meteor shower peak tonight at 11:00 PM."

## Troubleshooting

If you encounter issues, check the following:

1. **Logs**: Review the log file specified in the configuration (`/var/log/nsp-ntfy.log`).
2. **MQTT Broker**: Ensure the MQTT broker is running and accessible.
3. **Configuration**: Verify the configuration files for any errors.
4. **Service Status**: Check the status of the NSP-NTFY service:

```bash
sudo systemctl status nsp-ntfy
```

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

Don't forget to give the project a star! Thanks again!

1. Fork the Project
1. Create your Feature Branch (git checkout -b feature/AmazingFeature)
1. Commit your Changes (git commit -m 'Add some AmazingFeature')
1. Push to the Branch (git push origin feature/AmazingFeature)
1. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
