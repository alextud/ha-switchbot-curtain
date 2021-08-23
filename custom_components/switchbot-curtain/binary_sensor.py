"""Support for SwitchBot binary sensors."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.switchbot.coordinator import (
    SwitchbotDataUpdateCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN, MANUFACTURER, BinarySensorType

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Switchbot curtain based on a config entry."""
    coordinator: SwitchbotDataUpdateCoordinator = hass.data[DOMAIN][DATA_COORDINATOR]

    binary_sensors = []

    for idx in coordinator.data:
        if idx == entry.unique_id.lower():

            if coordinator.data[idx].get("data"):
                for item in coordinator.data[idx].get("data"):
                    if item in BinarySensorType.__members__:
                        sensor_type_name = getattr(BinarySensorType, item).value
                        binary_sensors.append(
                            SwitchBotBinarySensor(
                                coordinator,
                                idx,
                                item,
                                sensor_type_name,
                                entry.data[CONF_MAC],
                                entry.data[CONF_NAME],
                            )
                        )

    async_add_entities(binary_sensors)


class SwitchBotBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Switchbot binary sensor."""

    coordinator: SwitchbotDataUpdateCoordinator

    def __init__(
        self,
        coordinator: SwitchbotDataUpdateCoordinator,
        idx: str,
        item: str,
        sensor_type_name: str,
        mac: str,
        switchbot_name: str,
    ) -> None:
        """Initialize the Switchbot sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._sensor = item
        self.switchbot_name = switchbot_name
        self._mac = mac
        self._sensor_type = sensor_type_name
        self._model = self.coordinator.data[self._idx]["modelName"]

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._mac.replace(':', '')}-{self._sensor}"

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return f"{self.switchbot_name}.{self._sensor}"

    @property
    def device_class(self) -> str | None:
        """Return the class of this device."""
        return self._sensor_type

    @property
    def state(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data[self._idx]["data"][self._sensor]

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._mac.replace(":", ""))},
            "name": self.switchbot_name,
            "model": self._model,
            "manufacturer": MANUFACTURER,
        }
