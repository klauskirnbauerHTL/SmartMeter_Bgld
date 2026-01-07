"""The Smart Meter Burgenland integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .smartmeter_client import SmartMeterClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

SCAN_INTERVAL = timedelta(hours=1)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Meter Burgenland from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = SmartMeterClient(
        username=entry.data["username"],
        password=entry.data["password"],
        headless=entry.data.get("headless", True),
        price_per_kwh=entry.data.get("price_per_kwh", 0.15)
    )

    async def async_update_data():
        """Fetch data from Smart Meter Portal."""
        try:
            return await hass.async_add_executor_job(client.get_consumption_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Smart Meter Portal: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="smartmeter_burgenland",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
