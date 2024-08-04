import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .api import SleepmeAPI

_LOGGER = logging.getLogger(__name__)

class SleepmeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_key = user_input["api_key"]
            api = SleepmeAPI(api_key)

            try:
                devices = await self.hass.async_add_executor_job(api.get_devices)
                if devices:
                    return self.async_create_entry(title="Sleep.me", data={"api_key": api_key})
                else:
                    errors["base"] = "no_devices"
            except Exception as e:
                _LOGGER.error(f"Error fetching devices: {e}")
                errors["base"] = "cannot_connect"

        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required("api_key"): str,
        }), errors=errors)
