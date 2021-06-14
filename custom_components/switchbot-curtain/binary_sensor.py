"""Support for SwitchBot binary sensors."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN, MANUFACTURER

# Initialize the logger
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Switchbot curtain based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    binary_sensors = []

    for idx in coordinator.data:
        if idx == entry.unique_id.lower():

            if coordinator.data[idx].get("serviceData"):
                for items in coordinator.data[idx].get("serviceData"):
                    if items == "calibration":
                        binary_sensors.append(
                            SwitchBotBinarySensor(
                                coordinator,
                                idx,
                                entry.data[CONF_MAC],
                                entry.data[CONF_NAME],
                            )
                        )

    async_add_entities(binary_sensors)


class SwitchBotBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Switchbot binary sensor."""

    def __init__(self, coordinator, idx, mac, name, sensor_type=None) -> None:
        """Initialize the Switchbot sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._name = name
        self._mac = mac
        self._sensor_type = sensor_type
        self._sensor_name = f"{self._name}-calibration"
        self._model = self.coordinator.data[self._idx]["serviceData"]["modelName"]

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._mac.replace(':', '')}-calibration"

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._sensor_name

    @property
    def device_class(self) -> str:
        """Return the class of this device."""
        return self._sensor_type

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._idx]["serviceData"]["calibration"]

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._mac.replace(":", ""))},
            "name": self._name,
            "model": self._model,
            "manufacturer": MANUFACTURER,
        }
