import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, BINARY_SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for device_id, device in coordinator.data.items():
        for sensor_type in BINARY_SENSOR_TYPES:
            entities.append(SleepmeBinarySensor(coordinator, device["info"], device["state"], sensor_type))
    
    async_add_entities(entities, True)

class SleepmeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, device_info, device_state, sensor_type):
        super().__init__(coordinator)
        self._device_info = device_info
        self._device_state = device_state
        self._sensor_type = sensor_type
        self._name = f"{device_info['name']} {BINARY_SENSOR_TYPES[sensor_type]}"
        self._unique_id = f"{device_info['id']}_{sensor_type}"
        self._state = None

        _LOGGER.debug(f"Initializing SleepmeBinarySensor with device info: {device_info}, state: {device_state}, and sensor type: {sensor_type}")

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def is_on(self):
        try:
            status = self.coordinator.data[self._device_info["id"]]["state"].get("status", {})
            _LOGGER.debug(f"Status for binary sensor {self._unique_id}: {status}")
            if self._sensor_type == "is_water_low":
                return status.get("is_water_low")
            elif self._sensor_type == "is_connected":
                return status.get("is_connected")
        except KeyError:
            _LOGGER.error(f"Error fetching state for binary sensor {self._unique_id}: {self._device_state}")
            return None
