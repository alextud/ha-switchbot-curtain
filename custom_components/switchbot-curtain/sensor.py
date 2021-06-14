"""Support for SwitchBot sensors."""
from __future__ import annotations

import logging

from homeassistant.const import CONF_MAC, CONF_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN, MANUFACTURER

# Initialize the logger
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Switchbot sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]

    sensors = []

    for idx in coordinator.data:
        if idx == entry.unique_id:
            if coordinator.data[idx].get("rssi"):
                sensors.append(
                    SwitchBotSensor(
                        coordinator,
                        idx,
                        entry.data[CONF_MAC],
                        entry.data[CONF_NAME],
                        sensor_type="signal_strength",
                    )
                )

            if coordinator.data[idx].get("serviceData"):
                for items in coordinator.data[idx].get("serviceData"):
                    if items == "battery":
                        sensors.append(
                            SwitchBotSensor(
                                coordinator,
                                idx,
                                entry.data[CONF_MAC],
                                entry.data[CONF_NAME],
                                sensor_type="battery",
                            )
                        )

                    if items == "lightLevel":
                        sensors.append(
                            SwitchBotSensor(
                                coordinator,
                                idx,
                                entry.data[CONF_MAC],
                                entry.data[CONF_NAME],
                                sensor_type="lightLevel",
                            )
                        )

    async_add_entities(sensors)


class SwitchBotSensor(CoordinatorEntity, Entity):
    """Representation of a Switchbot sensor."""

    def __init__(self, coordinator, idx, mac, name, sensor_type=None) -> None:
        """Initialize the Switchbot sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._name = name
        self._mac = mac
        self._sensor_type = sensor_type
        self._sensor_name = f"{self._name}_{self._sensor_type}"
        self._model = self.coordinator.data[self._idx]["serviceData"]["modelName"]

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return f"{self._mac.replace(':', '')}-{self._sensor_type}"

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
        if self._sensor_type == "battery":
            return self.coordinator.data[self._idx]["serviceData"]["battery"]

        if self._sensor_type == "signal_strength":
            return self.coordinator.data[self._idx]["rssi"]

        return self.coordinator.data[self._idx]["serviceData"]["lightLevel"]

    @property
    def device_info(self):
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._mac.replace(":", ""))},
            "name": self._name,
            "model": self._model,
            "manufacturer": MANUFACTURER,
        }
