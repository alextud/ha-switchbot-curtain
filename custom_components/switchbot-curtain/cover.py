"""Support for SwitchBot curtains."""
from __future__ import annotations

import logging
from typing import Any
import threading

# pylint: disable=import-error
import switchbot
from bluepy.btle import BTLEInternalError

from homeassistant.components.cover import (
    ATTR_POSITION,
    DEVICE_CLASS_CURTAIN,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
    CoverEntity,
)
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_PASSWORD, CONF_SENSOR_TYPE
from homeassistant.helpers.restore_state import RestoreEntity

from .const import ATTR_CURTAIN, DOMAIN, MANUFACTURER

DEFAULT_RETRY_COUNT = 3
DEFAULT_RETRY_TIMEOUT = 10
DEFAULT_TIME_BETWEEN_UPDATE_COMMAND = 60
CONNECT_LOCK = threading.Lock()

# Initialize the logger
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Switchbot curtain based on a config entry."""

    device = []

    if entry.data[CONF_SENSOR_TYPE] == ATTR_CURTAIN:
        device.append(
            SwitchBotCurtain(
                entry.data[CONF_MAC],
                entry.data[CONF_NAME],
                entry.data.get(CONF_PASSWORD, None),
            )
        )

    async_add_entities(device)


class SwitchBotCurtain(CoverEntity, RestoreEntity):
    """Representation of a Switchbot."""

    def __init__(self, mac, name, password=None) -> None:
        """Initialize the Switchbot."""

        self._state = None
        self._last_run_success = None
        self._battery = None
        self._light = None
        self._name = name
        self._mac = mac
        self._device = switchbot.SwitchbotCurtain(mac=mac, password=password)
        self._pos = 0

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if not state:
            return
        _LOGGER.info("Switchbot state %s", state)
        self._state = state.state

        if "current_position" in state.attributes:
            self._pos = state.attributes["current_position"]

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return True

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._mac.replace(":", "")

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def device_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "last_run_success": self._last_run_success,
            "battery": self._battery,
            "light": self._light,
        }

    @property
    def device_class(self) -> str:
        """Return the class of this device."""
        return DEVICE_CLASS_CURTAIN

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP | SUPPORT_SET_POSITION

    @property
    def is_closed(self):
        """Return if the cover is closed."""
        return self.current_cover_position <= 0

    def open_cover(self, **kwargs) -> None:
        """Open the curtain with using this device."""

        _LOGGER.info("Switchbot to open curtain %s", self._mac)

        if self._device.open():
            self._last_run_success = True
        else:
            self._last_run_success = False

    def close_cover(self, **kwargs) -> None:
        """Close the curtain with using this device."""

        _LOGGER.info("Switchbot to close the curtain %s", self._mac)

        if self._device.close():
            self._last_run_success = True
        else:
            self._last_run_success = False

    def stop_cover(self, **kwargs) -> None:
        """Stop the moving of this device."""

        _LOGGER.info("Switchbot to stop %s", self._mac)

        if self._device.stop():
            self._last_run_success = True
        else:
            self._last_run_success = False

    def set_cover_position(self, **kwargs):
        """Move the cover shutter to a specific position."""
        position = kwargs.get(ATTR_POSITION)

        _LOGGER.info("Switchbot to move at %d %s", position, self._mac)

        if self._device.set_position(position):
            self._last_run_success = True
        else:
            self._last_run_success = False

    @property
    def current_cover_position(self):
        """Return the current position of cover shutter."""
        return self._device.get_position()

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._mac.replace(":", ""))},
            "name": self._name,
            "model": "Curtain",
            "manufacturer": MANUFACTURER,
        }

    def update(self):
        """Update device attributes."""
        try:
            with CONNECT_LOCK:
                self._device.update()
                self._light = self._device.get_light_level()
                self._battery = self._device.get_battery_percent()

        except BTLEInternalError as err:
            raise BTLEInternalError(err) from err
