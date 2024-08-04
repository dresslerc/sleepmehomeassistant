import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for device_id, device in coordinator.data.items():
        for sensor_type in SENSOR_TYPES:
            entities.append(SleepmeSensor(coordinator, device["info"], device["state"], sensor_type))
    
    async_add_entities(entities, True)

class SleepmeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_info, device_state, sensor_type):
        super().__init__(coordinator)
        self._device_info = device_info
        self._device_state = device_state
        self._sensor_type = sensor_type
        self._name = f"{device_info['name']} {SENSOR_TYPES[sensor_type]}"
        self._unique_id = f"{device_info['id']}_{sensor_type}"
        self._state = None

        _LOGGER.debug(f"Initializing SleepmeSensor with device info: {device_info}, state: {device_state}, and sensor type: {sensor_type}")

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        try:
            status = self.coordinator.data[self._device_info["id"]]["state"].get("status", {})
            _LOGGER.debug(f"Status for sensor {self._unique_id}: {status}")
            if self._sensor_type == "water_temperature_f":
                return status.get("water_temperature_f")
            elif self._sensor_type == "water_temperature_c":
                return status.get("water_temperature_c")
            elif self._sensor_type == "water_level":
                return status.get("water_level")
        except KeyError:
            _LOGGER.error(f"Error fetching state for sensor {self._unique_id}: {self._device_state}")
            return None

    @property
    def unit_of_measurement(self):
        if self._sensor_type == "water_temperature_f":
            return UnitOfTemperature.FAHRENHEIT
        elif self._sensor_type == "water_temperature_c":
            return UnitOfTemperature.CELSIUS
        elif self._sensor_type == "water_level":
            return PERCENTAGE

    @property
    def device_class(self):
        if self._sensor_type in ["water_temperature_f", "water_temperature_c"]:
            return SensorDeviceClass.TEMPERATURE
