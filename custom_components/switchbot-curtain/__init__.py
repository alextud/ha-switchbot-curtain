"""Support for Switchbot devices."""
from .const import (
    CONF_RETRY_COUNT,
    CONF_RETRY_TIMEOUT,
    CONF_TIME_BETWEEN_UPDATE_COMMAND,
    DEFAULT_RETRY_COUNT,
    DEFAULT_RETRY_TIMEOUT,
    DEFAULT_TIME_BETWEEN_UPDATE_COMMAND,
    DOMAIN,
)

PLATFORMS = ["switch", "cover"]


async def async_setup_entry(hass, entry):
    """Set up Switchbot from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    if not entry.options:
        options = {
            CONF_TIME_BETWEEN_UPDATE_COMMAND: entry.data.get(
                CONF_TIME_BETWEEN_UPDATE_COMMAND, DEFAULT_TIME_BETWEEN_UPDATE_COMMAND
            ),
            CONF_RETRY_COUNT: entry.data.get(CONF_RETRY_COUNT, DEFAULT_RETRY_COUNT),
            CONF_RETRY_TIMEOUT: entry.data.get(
                CONF_RETRY_TIMEOUT, DEFAULT_RETRY_TIMEOUT
            ),
        }
        hass.config_entries.async_update_entry(entry, options=options)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
