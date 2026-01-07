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

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

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


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Smart Meter Burgenland."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Wenn Benutzername oder Passwort geändert wurde, validiere die Verbindung
            if (
                user_input.get(CONF_USERNAME) != self.config_entry.data.get(CONF_USERNAME)
                or user_input.get(CONF_PASSWORD) != self.config_entry.data.get(CONF_PASSWORD)
            ):
                try:
                    await validate_input(self.hass, user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"

            if not errors:
                # Update config entry data
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={**self.config_entry.data, **user_input},
                )
                return self.async_create_entry(title="", data={})

        # Zeige Formular mit aktuellen Werten
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_USERNAME,
                    default=self.config_entry.data.get(CONF_USERNAME)
                ): str,
                vol.Required(
                    CONF_PASSWORD,
                    default=self.config_entry.data.get(CONF_PASSWORD)
                ): str,
                vol.Optional(
                    CONF_PRICE_PER_KWH,
                    default=self.config_entry.data.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH)
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_HEADLESS,
                    default=self.config_entry.data.get(CONF_HEADLESS, True)
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
