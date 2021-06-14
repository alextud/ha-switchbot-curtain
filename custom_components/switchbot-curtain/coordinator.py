"""Provides the switchbot DataUpdateCoordinator."""
import asyncio
from datetime import timedelta
import logging

from bluepy.btle import BTLEDisconnectError, BTLEManagementError
from switchbot import SwitchbotDevices

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

CONNECT_LOCK = asyncio.Lock()

_LOGGER = logging.getLogger(__name__)


class SwitchbotDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching switchbot data."""

    def __init__(self, hass: HomeAssistant, *, api: SwitchbotDevices) -> None:
        """Initialize global switchbot data updater."""
        self.switchbots = api
        update_interval = timedelta(seconds=30)

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    def _update_data(self) -> SwitchbotDevices:
        """Fetch data from Switchbot via Switchbots Class."""

        switchbot_devices = self.switchbots.discover()

        return switchbot_devices

    async def _async_update_data(self):
        """Fetch data from switchbot."""
        try:
            async with CONNECT_LOCK:
                return await self.hass.async_add_executor_job(self._update_data)

        except (BTLEManagementError, BTLEDisconnectError) as error:
            raise UpdateFailed(f"Invalid response from API: {error}") from error
