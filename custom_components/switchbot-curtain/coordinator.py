"""Provides the switchbot DataUpdateCoordinator."""
import asyncio
from datetime import timedelta
import logging

from switchbot import GetSwitchbotDevices

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
        api: GetSwitchbotDevices,
    ) -> None:
        """Initialize global switchbot data updater."""
        self.switchbot_device = api
        self.update_interval = timedelta(seconds=update_interval)

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval
        )

    def _update_data(self):
        """get switchbot services data."""
        switchbot_device = self.switchbot_device

        return switchbot_device

    async def _async_update_data(self):
        """Fetch data from switchbot."""

        async with CONNECT_LOCK:
            return await self.hass.async_add_executor_job(self._update_data)
