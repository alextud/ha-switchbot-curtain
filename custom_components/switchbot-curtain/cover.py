"""Support for SwitchBot curtains."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

# pylint: disable=import-error
import switchbot

from homeassistant.components.cover import (
    ATTR_CURRENT_POSITION,
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

from .const import (
    ATTR_CURTAIN,
    CONF_RETRY_COUNT,
    CONF_RETRY_TIMEOUT,
    CONF_TIME_BETWEEN_UPDATE_COMMAND,
    DOMAIN,
    MANUFACTURER,
)

CONNECT_LOCK = asyncio.Lock()
SCAN_INTERVAL = timedelta(seconds=35)
PARALLEL_UPDATES = 1

# Initialize the logger
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Switchbot curtain based on a config entry."""

    device = []

    switchbot.DEFAULT_RETRY_COUNT = entry.options[CONF_RETRY_COUNT]
    switchbot.DEFAULT_RETRY_TIMEOUT = entry.options[CONF_RETRY_TIMEOUT]
    switchbot.DEFAULT_TIME_BETWEEN_UPDATE_COMMAND = entry.options[
        CONF_TIME_BETWEEN_UPDATE_COMMAND
    ]

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

        if ATTR_CURRENT_POSITION in state.attributes:
            self._pos = state.attributes[ATTR_CURRENT_POSITION]

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
        return self._pos <= 10

    async def async_open_cover(self, **kwargs) -> None:
        """Open the curtain with using this device."""

        _LOGGER.info("Switchbot to open curtain %s", self._mac)

        update_ok = await self.hass.async_add_executor_job(self._device.open)

        if update_ok:
            self._last_run_success = True
        else:
            self._last_run_success = False

    async def async_close_cover(self, **kwargs) -> None:
        """Close the curtain with using this device."""

        _LOGGER.info("Switchbot to close the curtain %s", self._mac)

        update_ok = await self.hass.async_add_executor_job(self._device.close)

        if update_ok:
            self._last_run_success = True
        else:
            self._last_run_success = False

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop the moving of this device."""

        _LOGGER.info("Switchbot to stop %s", self._mac)

        update_ok = await self.hass.async_add_executor_job(self._device.stop)

        if update_ok:
            self._last_run_success = True
        else:
            self._last_run_success = False

    async def async_set_cover_position(self, **kwargs):
        """Move the cover shutter to a specific position."""
        position = kwargs.get(ATTR_POSITION)

        _LOGGER.info("Switchbot to move at %d %s", position, self._mac)

        update_ok = await self.hass.async_add_executor_job(
            self._device.set_position, position
        )

        if update_ok:
            self._last_run_success = True
        else:
            self._last_run_success = False

    @property
    def current_cover_position(self):
        """Return the current position of cover shutter."""
        return self._pos

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._mac.replace(":", ""))},
            "name": self._name,
            "model": "Curtain",
            "manufacturer": MANUFACTURER,
        }

    async def async_update(self):
        """Update device attributes."""
        async with CONNECT_LOCK:
            await self.hass.async_add_executor_job(self._device.update)

        self._light = await self.hass.async_add_executor_job(
            self._device.get_light_level
        )
        self._battery = await self.hass.async_add_executor_job(
            self._device.get_battery_percent
        )
        self._pos = await self.hass.async_add_executor_job(self._device.get_position)
