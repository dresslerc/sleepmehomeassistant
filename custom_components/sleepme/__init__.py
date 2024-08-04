import logging
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN
from .api import SleepmeAPI

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api_key = entry.data["api_key"]
    api = SleepmeAPI(api_key)

    async def async_update_data():
        try:
            devices = await hass.async_add_executor_job(api.get_devices)
            device_data = {}
            for device in devices:
                state = await hass.async_add_executor_job(api.get_device_state, device["id"])
                device_data[device["id"]] = {
                    "info": device,
                    "state": state
                }
            return device_data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sleepme",
        update_method=async_update_data,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    for platform in ["climate", "sensor", "binary_sensor"]:
        await hass.config_entries.async_forward_entry_setup(entry, platform)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "climate")
    unload_ok = unload_ok and await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    unload_ok = unload_ok and await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
