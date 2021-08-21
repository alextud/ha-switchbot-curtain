"""Support for SwitchBot curtains."""
from __future__ import annotations

import logging

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
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CURTAIN,
    CONF_RETRY_COUNT,
    DATA_COORDINATOR,
    DOMAIN,
    MANUFACTURER,
)

PARALLEL_UPDATES = 1
# Initialize the logger
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up Switchbot curtain based on a config entry."""
    coordinator = hass.data[DOMAIN][DATA_COORDINATOR]

    curtain_device = []

    if entry.data[CONF_SENSOR_TYPE] == ATTR_CURTAIN:
        for idx in coordinator.data:
            if idx == entry.unique_id.lower():

                curtain_device.append(
                    SwitchBotCurtain(
                        coordinator,
                        idx,
                        entry.data[CONF_MAC],
                        entry.data[CONF_NAME],
                        entry.data.get(CONF_PASSWORD, None),
                        entry.options[CONF_RETRY_COUNT],
                    )
                )

    async_add_entities(curtain_device)


class SwitchBotCurtain(CoordinatorEntity, CoverEntity, RestoreEntity):
    """Representation of a Switchbot."""

    def __init__(self, coordinator, idx, mac, name, password, retry_count) -> None:
        """Initialize the Switchbot."""
        super().__init__(coordinator)
        self._last_run_success = None
        self._idx = idx
        self.switchbot_name = name
        self._mac = mac
        self._model = self.coordinator.data[self._idx]["modelName"]
        self._device = self.coordinator.switchbot_api.SwitchbotCurtain(
            mac=mac, password=password, retry_count=retry_count
        )

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        if ATTR_CURRENT_POSITION in last_state.attributes:
            self._attr_current_cover_position = last_state.attributes[
                ATTR_CURRENT_POSITION
            ]
            self._attr_state = last_state.state
            self._last_run_success = last_state.attributes["last_run_success"]

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
        return self.switchbot_name

    @property
    def device_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {"last_run_success": self._last_run_success, "MAC": self._mac}

    @property
    def device_class(self) -> str:
        """Return the class of this device."""
        return DEVICE_CLASS_CURTAIN

    @property
    def supported_features(self) -> str:
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP | SUPPORT_SET_POSITION

    @property
    def is_closed(self) -> int:
        """Return if the cover is closed."""
        return self.coordinator.data[self._idx]["data"]["position"] <= 20

    async def async_open_cover(self, **kwargs) -> None:
        """Open the curtain."""

        _LOGGER.info("Switchbot to open curtain %s", self._mac)

        async with self.coordinator.connect_lock:
            update_ok = await self.hass.async_add_executor_job(self._device.open)

            if update_ok:
                self._last_run_success = True
                self.coordinator.async_request_refresh()
            else:
                self._last_run_success = False

    async def async_close_cover(self, **kwargs) -> None:
        """Close the curtain."""

        _LOGGER.info("Switchbot to close the curtain %s", self._mac)

        async with self.coordinator.connect_lock:
            update_ok = await self.hass.async_add_executor_job(self._device.close)

            if update_ok:
                self._last_run_success = True
                self.coordinator.async_request_refresh()
            else:
                self._last_run_success = False

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop the moving of this device."""

        _LOGGER.info("Switchbot to stop %s", self._mac)

        async with self.coordinator.connect_lock:
            update_ok = await self.hass.async_add_executor_job(self._device.stop)

            if update_ok:
                self._last_run_success = True
                self.coordinator.async_request_refresh()
            else:
                self._last_run_success = False

    async def async_set_cover_position(self, **kwargs) -> None:
        """Move the cover shutter to a specific position."""
        position = kwargs.get(ATTR_POSITION)

        _LOGGER.info("Switchbot to move at %d %s", position, self._mac)

        async with self.coordinator.connect_lock:
            update_ok = await self.hass.async_add_executor_job(
                self._device.set_position, position
            )

            if update_ok:
                self._last_run_success = True
                self.coordinator.async_request_refresh()
            else:
                self._last_run_success = False

    @property
    def current_cover_position(self) -> int:
        """Return the current position of cover shutter."""
        return self.coordinator.data[self._idx]["data"]["position"]

    @property
    def device_info(self) -> dict:
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._mac.replace(":", ""))},
            "name": self.switchbot_name,
            "model": self._model,
            "manufacturer": MANUFACTURER,
        }
