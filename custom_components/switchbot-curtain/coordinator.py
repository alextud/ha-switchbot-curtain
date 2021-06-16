"""Provides the switchbot DataUpdateCoordinator."""
import asyncio
from datetime import timedelta
import logging

from bluepy.btle import BTLEDisconnectError, BTLEManagementError
import switchbot

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

CONNECT_LOCK = asyncio.Lock()

_LOGGER = logging.getLogger(__name__)


class SwitchbotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching switchbot data."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        update_interval: int,
        api: switchbot.SwitchbotDevice,
    ) -> None:
        """Initialize global switchbot data updater."""
        self.switchbot_device = api
        self.update_interval = timedelta(seconds=update_interval)

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval
        )

    def _update_data(self) -> switchbot.SwitchbotDevice:
        """Fetch data from Switchbot via Switchbots Class."""

        switchbot_devices = self.switchbot_device.discover()

        return switchbot_devices

    async def _async_update_data(self):
        """Fetch data from switchbot."""
        try:
            async with CONNECT_LOCK:
                return await self.hass.async_add_executor_job(self._update_data)

        except (BTLEManagementError, BTLEDisconnectError) as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
