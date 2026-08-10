"""Config flow for TV Control Center integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

DOMAIN = "tv_control_center"

class TvControlCenterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TV Control Center."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial user step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"Smart TV ({user_input['host']})",
                data=user_input,
            )

        data_schema = vol.Schema({
            vol.Required("host", default="192.168.2.122"): str,
            vol.Required("port", default=5555): int,
            vol.Optional("name", default="Living Room TV"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
