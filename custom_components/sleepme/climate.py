import logging
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature
)
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .api import SleepmeAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    api = SleepmeAPI(config_entry.data["api_key"])
    entities = []

    for device_id, device in coordinator.data.items():
        entities.append(SleepmeClimate(coordinator, api, device["info"], device["state"]))

    async_add_entities(entities, True)

class SleepmeClimate(CoordinatorEntity, ClimateEntity):
    def __init__(self, coordinator, api, device_info, device_state):
        super().__init__(coordinator)
        self._api = api
        self._device_info = device_info
        self._device_state = device_state
        self._name = device_info["name"]
        self._state = device_state.get("control", {}).get("thermal_control_status") == "active"
        self._target_temperature = device_state.get("control", {}).get("set_temperature_f")
        self._current_temperature = device_state.get("status", {}).get("water_temperature_f")

        _LOGGER.debug(f"Initializing SleepmeClimate with device info: {device_info} and state: {device_state}")

    @property
    def supported_features(self):
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def hvac_modes(self):
        return [HVACMode.OFF, HVACMode.HEAT_COOL]

    @property
    def min_temp(self):
        return 55

    @property
    def max_temp(self):
        return 115

    @property
    def name(self):
        return self._name

    @property
    def temperature_unit(self):
        return UnitOfTemperature.FAHRENHEIT

    @property
    def current_temperature(self):
        try:
            status = self.coordinator.data[self._device_info["id"]]["state"].get("status", {})
            _LOGGER.debug(f"Status for device {self._device_info['id']}: {status}")
            self._current_temperature = status.get("water_temperature_f")
            return status.get("water_temperature_f")
        except KeyError:
            _LOGGER.error(f"Error fetching current temperature for device {self._device_info['id']}: {self._device_state}")
            return None


    @property
    def target_temperature(self):
        return self._target_temperature


    async def async_set_temperature(self, **kwargs):
        temperature = kwargs.get("temperature")
        if temperature is not None:
            temperature = int(temperature)
            _LOGGER.debug(f"Setting target temperature to {temperature}F")
            await self.hass.async_add_executor_job(
                self._api.set_device_temperature, self._device_info["id"], temperature
            )
            self._target_temperature = temperature
            self.async_write_ha_state()  # Update the state immediately

    @property
    def hvac_mode(self):
        #return HVACMode.HEAT_COOL if self._state else HVACMode.OFF
        try:
            control = self.coordinator.data[self._device_info["id"]]["state"].get("control", {})
            _LOGGER.debug(f"Control for device {self._device_info['id']}: {control}")
            return HVACMode.HEAT_COOL if control.get("thermal_control_status") == "active" else HVACMode.OFF
        except KeyError:
            _LOGGER.error(f"Error fetching HVAC mode for device {self._device_info['id']}: {self._device_state}")
            return HVACMode.OFF
        

    async def async_set_hvac_mode(self, hvac_mode):
        mode = "active" if hvac_mode == HVACMode.HEAT_COOL else "standby"
        _LOGGER.debug(f"Setting HVAC mode to {mode}")
        await self.hass.async_add_executor_job(
            self._api.set_device_mode, self._device_info["id"], mode
        )

        if (mode == "active"):
            self._state = HVACMode.HEAT_COOL
        else:
            self._state = HVACMode.OFF
       
        self.async_write_ha_state()  # Update the state immediately

    async def async_update(self):
        await self.coordinator.async_request_refresh()
        device_state = self.coordinator.data[self._device_info["id"]]["state"]
        self._state = device_state.get("control", {}).get("thermal_control_status") == "active"
        self._target_temperature = device_state.get("control", {}).get("set_temperature_f")
        self._current_temperature = device_state.get("status", {}).get("water_temperature_f")
