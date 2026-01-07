"""Config flow for Smart Meter Burgenland integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_HEADLESS, CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH, DOMAIN
from .smartmeter_client import SmartMeterClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_PRICE_PER_KWH, default=DEFAULT_PRICE_PER_KWH): vol.Coerce(float),
        vol.Optional(CONF_HEADLESS, default=True): bool,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = SmartMeterClient(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        headless=data.get(CONF_HEADLESS, True),
        price_per_kwh=data.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH)
    )

    # Test the connection
    try:
        result = await hass.async_add_executor_job(client.test_connection)
        if not result:
            raise InvalidAuth
    except Exception as err:
        _LOGGER.error("Error testing connection: %s", err)
        raise CannotConnect from err
    finally:
        await hass.async_add_executor_job(client.close)

    return {"title": f"Smart Meter ({data[CONF_USERNAME]})"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Meter Burgenland."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
