"""Support for Switchbot bot."""
from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any

# pylint: disable=import-error
import switchbot
import voluptuous as vol

from homeassistant.components.switch import (
    DEVICE_CLASS_SWITCH,
    PLATFORM_SCHEMA,
    SwitchEntity,
)
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import CONF_MAC, CONF_NAME, CONF_PASSWORD, CONF_SENSOR_TYPE
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    ATTR_BOT,
    CONF_RETRY_COUNT,
    CONF_RETRY_TIMEOUT,
    CONF_TIME_BETWEEN_UPDATE_COMMAND,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
)

CONNECT_LOCK = asyncio.Lock()
SCAN_INTERVAL = timedelta(seconds=35)
PARALLEL_UPDATES = 1

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MAC): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Import yaml config and initiates config flow for Switchbot devices."""

    # Check if entry config exists and skips import if it does.
    if hass.config_entries.async_entries(DOMAIN):
        return

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={
                CONF_NAME: config[CONF_NAME],
                CONF_PASSWORD: config.get(CONF_PASSWORD, None),
                CONF_MAC: config[CONF_MAC],
                CONF_SENSOR_TYPE: ATTR_BOT,
            },
        )
    )


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Switchbot based on a config entry."""

    device = []

    switchbot.DEFAULT_RETRY_COUNT = entry.options[CONF_RETRY_COUNT]
    switchbot.DEFAULT_RETRY_TIMEOUT = entry.options[CONF_RETRY_TIMEOUT]
    switchbot.DEFAULT_TIME_BETWEEN_UPDATE_COMMAND = entry.options[
        CONF_TIME_BETWEEN_UPDATE_COMMAND
    ]

    if entry.data[CONF_SENSOR_TYPE] == ATTR_BOT:
        device.append(
            SwitchBot(
                entry.data[CONF_MAC],
                entry.data[CONF_NAME],
                entry.data.get(CONF_PASSWORD, None),
            )
        )

    async_add_entities(device)


class SwitchBot(SwitchEntity, RestoreEntity):
    """Representation of a Switchbot."""

    def __init__(self, mac, name, password=None) -> None:
        """Initialize the Switchbot."""

        self._state = None
        self._last_run_success = None
        self._name = name
        self._battery = None
        self._mode = None
        self._mac = mac
        self._device = switchbot.Switchbot(mac=mac, password=password)
        self._device_class = DEVICE_CLASS_SWITCH

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if not state:
            return
        self._state = state.state

    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        update_ok = await self.hass.async_add_executor_job(self._device.turn_on)

        if update_ok:
            self._last_run_success = True
        else:
            self._last_run_success = False

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        update_ok = await self.hass.async_add_executor_job(self._device.turn_off)

        if update_ok:
            self._last_run_success = True
        else:
            self._last_run_success = False

    async def async_toggle(self, **kwargs) -> None:
        """Toggle for switchbot in toggle mode."""
        update_ok = await self.hass.async_add_executor_job(self._device.press)

        if update_ok:
            self._last_run_success = True
        else:
            self._last_run_success = False

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return True

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._state

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
            "mode": self._mode,
        }

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._mac.replace(":", ""))},
            "name": self._name,
            "model": "Bot",
            "manufacturer": MANUFACTURER,
        }

    async def async_update(self):
        """Update device attributes."""
        async with CONNECT_LOCK:
            await self.hass.async_add_executor_job(self._device.update)

        self._state = await self.hass.async_add_executor_job(self._device.is_on)
        self._battery = await self.hass.async_add_executor_job(
            self._device.get_battery_percent
        )
        self._mode = await self.hass.async_add_executor_job(self._device.switch_mode)

    @property
    def device_class(self):
        """Device class for the sensor."""
        return self._device_class
