# NSP Ntfy

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/joe-mccarthy/nsp-ntfy/build-and-test.yml)
![Coveralls](https://img.shields.io/coverallsCoverage/github/joe-mccarthy/nsp-ntfy)
![Sonar Quality Gate](https://img.shields.io/sonar/quality_gate/joe-mccarthy_nsp-ntfy?server=https%3A%2F%2Fsonarcloud.io)
[![GitHub Release](https://img.shields.io/github/v/release/joe-mccarthy/nsp-ntfy?sort=semver&cacheSeconds=1)](https://github.com/joe-mccarthy/nsp-ntfy/releases/latest)
![GitHub commits since latest release](https://img.shields.io/github/commits-since/joe-mccarthy/nsp-ntfy/latest?cacheSeconds=1)
[![GitHub License](https://img.shields.io/github/license/joe-mccarthy/nsp-ntfy?cacheSeconds=1)](LICENSE)

The Night Sky Pi can be configured to publish messages to a local MQTT broker. The NSP-NTFY module can be configured to listen to these notifactions and publish the notification field to [ntfy.sh](ntfy.sh). This is so push notifications can be recieved on other devices without having to make the broker on the device public with routing.

## Prerequisites

Before deploying the nsp-ntfy it's important to ensure that you have the following configured as there are dependencies. However the installation of an MQTT broker is optional I usually have it installed instead of needing to remember to do it when starting up other applications.

### Python

nsp-ntfy is written in Python and has been tested with the following Python versions:

- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

The [nsp-ntfy.sh](nsp-ntfy.sh) runs within a virtual environment based on what's on your system path.

### MQTT Broker

Night Sky Pi has the ability to publish events to an MQTT broker. The intent of this is so that other modules can react to the events to complete additional actions. Initially this broker will only run locally therefore only allow clients that reside on the same device as intended. Firstly we need to install MQTT on the Raspberry Pi.

```bash
sudo apt update && sudo apt upgrade
sudo apt install -y mosquitto
sudo apt install -y mosquitto-clients # Optional for testing locally
sudo systemctl enable mosquitto.service
sudo reboot # Just something I like to do, this is optional as well
```

The next step is to configure the nsp-ntfy to use the MQTT broker, as MQTT events are disabled by default. These configuration items are in the nsp configuration not the configuration of the nsp-ntfy module.

```json
"device" : {
    "mqtt" : {
        "enabled": true,
        "host": "127.0.0.1"
    }
}
```

## Running NSP-NTFY

It's recommended that nsp-ntfy is run as a service. This ensures that it doesn't stop of user logging off and on system restarts to do this carry out the following.

```bash
# current working directory is the nsp-ntfy repository.
sudo cp nsp.service /etc/systemd/system/nsp-ntfy.service
sudo nano /etc/systemd/system/nsp-ntfy.service
```

Next step is to update the service definition to the correct paths and running as the correct user.

```bash
[Unit]
Description=nsp-ntfy
After=network.target

[Service]
Type=Simple
# update this to be your current user
User=username 
# the location of the nsp-ntfy repository
WorkingDirectory=/home/username/repositories/nsp-ntfy/ 
# update these paths to be the location of the nsp-ntfy.sh 
# update argument to where you previously copied the json configuration.
ExecStart=/home/username/repositories/nsp-ntfy/nsp-ntfy.sh /home/username/nsp-ntfy-config.json /home/username/nsp-config.json 
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Next is to enable and start the service.

```sh
sudo systemctl daemon-reload
sudo systemctl start nsp-ntfy
sudo systemctl enable nsp-ntfy
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
