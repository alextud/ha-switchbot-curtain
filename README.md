# ha-switchbot-curtain
Controls switchbot curtain using Home Assistant

![](../main/switchbot.jpeg)

Supported operations:
  - open / close / stop
  - set position [0-100]%
  
Not supported:
  - read switchbot sensors / position
  - password

## Find mac address of your device on linux
```
sudo hcitool lescan
```

## Installation

1. Copy the files of this repository into homeassistant config directory.
2. Add the config to your configuration.yaml file as explained below.
3. Restart Home Assistant

## Example
```
cover:
  - platform: switchbot-curtain
    mac: XX:XX:XX:XX:XX:XX
```

## Debugging problems

```
logger:
  default: error
  logs:
    custom_components.switchbot-curtain: debug
```
