import requests
import logging

_LOGGER = logging.getLogger(__name__)

class SleepmeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.developer.sleep.me/v1"
        _LOGGER.debug(f"Using API Key: {self.api_key}")

    def _get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        _LOGGER.debug(f"Headers: {headers}")
        return headers

    def get_devices(self):
        try:
            response = requests.get(f"{self.base_url}/devices", headers=self._get_headers())
            response.raise_for_status()
            devices = response.json()
            if isinstance(devices, list):
                _LOGGER.debug(f"Fetched devices: {devices}")
                return devices
            else:
                _LOGGER.error(f"Unexpected response format: {devices}")
                raise ValueError("Unexpected response format")
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Failed to fetch devices: {e}")
            raise

    def get_device_state(self, device_id):
        try:
            url = f"{self.base_url}/devices/{device_id}"
            _LOGGER.debug(f"Fetching state for device ID: {device_id} from URL: {url}")
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                _LOGGER.error(f"Device not found: {device_id}")
            _LOGGER.error(f"Failed to fetch device state: {e}")
            raise
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Failed to fetch device state: {e}")
            raise

    def set_device_temperature(self, device_id, temperature):
        try:
            payload = {"set_temperature_f": temperature}
            _LOGGER.debug(f"Setting temperature for device {device_id} to {temperature}F with payload: {payload}")
            response = requests.patch(f"{self.base_url}/devices/{device_id}", headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Failed to set device temperature: {e}")
            raise

    def set_device_mode(self, device_id, mode):
        try:
            payload = {"thermal_control_status": mode}
            response = requests.patch(f"{self.base_url}/devices/{device_id}", headers=self._get_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _LOGGER.error(f"Failed to set device mode: {e}")
            raise
