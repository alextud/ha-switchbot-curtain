"""Constants for the switchbot integration."""
from enum import Enum

DOMAIN = "switchbot-curtain"
MANUFACTURER = "switchbot"

ATTR_CURTAIN = "curtain"
ATTR_BOT = "bot"
DEFAULT_NAME = "Switchbot"
DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_TIMEOUT = 1
DEFAULT_TIME_BETWEEN_UPDATE_COMMAND = 30

# Config Options
CONF_TIME_BETWEEN_UPDATE_COMMAND = "update_time"
CONF_RETRY_COUNT = "retry_count"
CONF_RETRY_TIMEOUT = "retry_timeout"

# Data
DATA_COORDINATOR = "coordinator"
DATA_UNDO_UPDATE_LISTENER = "undo_update_listener"
CMD_HELPER = "cmd_helper"


class SensorType(Enum):
    """Sensors and their types to expose in HA."""

    # pylint: disable=invalid-name
    lightLevel = "None"
    battery = "battery"
    rssi = "signal_strength"


class BinarySensorType(Enum):
    """Binary_sensors and their types to expose in HA."""

    # pylint: disable=invalid-name
    calibration = "None"
