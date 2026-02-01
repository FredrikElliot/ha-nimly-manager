"""Config flow for Nimlykoder integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_MQTT_TOPIC,
    CONF_SLOT_MIN,
    CONF_SLOT_MAX,
    CONF_RESERVED_SLOTS,
    CONF_AUTO_EXPIRE,
    CONF_CLEANUP_TIME,
    CONF_OVERWRITE_PROTECTION,
    DEFAULT_MQTT_TOPIC,
    DEFAULT_SLOT_MIN,
    DEFAULT_SLOT_MAX,
    DEFAULT_RESERVED_SLOTS,
    DEFAULT_AUTO_EXPIRE,
    DEFAULT_CLEANUP_TIME,
    DEFAULT_OVERWRITE_PROTECTION,
)

_LOGGER = logging.getLogger(__name__)


def _parse_reserved_slots(value: Any) -> list[int]:
    """Parse reserved slots from string or list."""
    if isinstance(value, list):
        return [int(x) for x in value if str(x).strip()]
    if isinstance(value, str):
        if not value.strip():
            return []
        return [int(x.strip()) for x in value.split(",") if x.strip()]
    return []


def _format_reserved_slots(slots: list[int]) -> str:
    """Format reserved slots list as comma-separated string."""
    return ", ".join(str(x) for x in slots)


class NimlykoderConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nimlykoder."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate slot range
            if user_input[CONF_SLOT_MIN] > user_input[CONF_SLOT_MAX]:
                errors["base"] = "invalid_slot_range"
            else:
                # Check if already configured
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                # Convert reserved_slots from string to list
                options = dict(user_input)
                options[CONF_RESERVED_SLOTS] = _parse_reserved_slots(
                    user_input.get(CONF_RESERVED_SLOTS, "")
                )

                return self.async_create_entry(
                    title=user_input.get("name", "Nimlykoder"),
                    data={},
                    options=options,
                )

        # Build schema with defaults
        data_schema = vol.Schema(
            {
                vol.Optional("name", default="Nimlykoder"): str,
                vol.Required(CONF_MQTT_TOPIC, default=DEFAULT_MQTT_TOPIC): str,
                vol.Required(CONF_SLOT_MIN, default=DEFAULT_SLOT_MIN): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=99)
                ),
                vol.Required(CONF_SLOT_MAX, default=DEFAULT_SLOT_MAX): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=99)
                ),
                vol.Required(
                    CONF_RESERVED_SLOTS,
                    default=_format_reserved_slots(DEFAULT_RESERVED_SLOTS),
                ): str,
                vol.Required(CONF_AUTO_EXPIRE, default=DEFAULT_AUTO_EXPIRE): bool,
                vol.Required(CONF_CLEANUP_TIME, default=DEFAULT_CLEANUP_TIME): str,
                vol.Required(
                    CONF_OVERWRITE_PROTECTION, default=DEFAULT_OVERWRITE_PROTECTION
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return NimlykoderOptionsFlow(config_entry)


class NimlykoderOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Nimlykoder."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate slot range
            if user_input[CONF_SLOT_MIN] > user_input[CONF_SLOT_MAX]:
                errors["base"] = "invalid_slot_range"
            else:
                # Convert reserved_slots from string to list
                options = dict(user_input)
                options[CONF_RESERVED_SLOTS] = _parse_reserved_slots(
                    user_input.get(CONF_RESERVED_SLOTS, "")
                )
                return self.async_create_entry(title="", data=options)

        # Get current options
        options = self.config_entry.options

        # Format reserved_slots for display
        current_reserved = options.get(CONF_RESERVED_SLOTS, DEFAULT_RESERVED_SLOTS)
        if isinstance(current_reserved, list):
            current_reserved = _format_reserved_slots(current_reserved)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_MQTT_TOPIC,
                    default=options.get(CONF_MQTT_TOPIC, DEFAULT_MQTT_TOPIC),
                ): str,
                vol.Required(
                    CONF_SLOT_MIN,
                    default=options.get(CONF_SLOT_MIN, DEFAULT_SLOT_MIN),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=99)),
                vol.Required(
                    CONF_SLOT_MAX,
                    default=options.get(CONF_SLOT_MAX, DEFAULT_SLOT_MAX),
                ): vol.All(vol.Coerce(int), vol.Range(min=0, max=99)),
                vol.Required(
                    CONF_RESERVED_SLOTS,
                    default=current_reserved,
                ): str,
                vol.Required(
                    CONF_AUTO_EXPIRE,
                    default=options.get(CONF_AUTO_EXPIRE, DEFAULT_AUTO_EXPIRE),
                ): bool,
                vol.Required(
                    CONF_CLEANUP_TIME,
                    default=options.get(CONF_CLEANUP_TIME, DEFAULT_CLEANUP_TIME),
                ): str,
                vol.Required(
                    CONF_OVERWRITE_PROTECTION,
                    default=options.get(
                        CONF_OVERWRITE_PROTECTION, DEFAULT_OVERWRITE_PROTECTION
                    ),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )
