"""Config flow for Nimlykoder integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_LOCK_ENTITY,
    CONF_SLOT_MIN,
    CONF_SLOT_MAX,
    CONF_RESERVED_SLOTS,
    CONF_AUTO_EXPIRE,
    CONF_CLEANUP_TIME,
    CONF_OVERWRITE_PROTECTION,
    CONF_PIN_LENGTH,
    CONF_PROTECT_SENSITIVE,
    CONF_Z2M_BASE_TOPIC,
    DEFAULT_SLOT_MIN,
    DEFAULT_SLOT_MAX,
    DEFAULT_RESERVED_SLOTS,
    DEFAULT_AUTO_EXPIRE,
    DEFAULT_CLEANUP_TIME,
    DEFAULT_OVERWRITE_PROTECTION,
    DEFAULT_PIN_LENGTH,
    DEFAULT_Z2M_BASE_TOPIC,
    ALLOWED_PIN_LENGTHS,
)
from .adapters.mqtt_z2m import (
    MqttZ2mAdapter,
    Zigbee2MqttProtectionError,
)
from .protection import resolve_z2m_device

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


def _valid_base_topic(value: Any) -> bool:
    """Return whether a configured Zigbee2MQTT base topic is a valid MQTT topic."""
    return (
        isinstance(value, str)
        and bool(value.strip().strip("/"))
        and "+" not in value
        and "#" not in value
    )


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
                # Convert pin_length from string (selector) to int
                options[CONF_PIN_LENGTH] = int(user_input.get(CONF_PIN_LENGTH, DEFAULT_PIN_LENGTH))

                return self.async_create_entry(
                    title=user_input.get("name", "Nimlykoder"),
                    data={},
                    options=options,
                )

        # Build schema with defaults
        data_schema = vol.Schema(
            {
                vol.Optional("name", default="Nimlykoder"): str,
                vol.Required(CONF_LOCK_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="lock")
                ),
                vol.Required(CONF_SLOT_MIN, default=DEFAULT_SLOT_MIN): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=99, mode="box")
                ),
                vol.Required(CONF_SLOT_MAX, default=DEFAULT_SLOT_MAX): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=99, mode="box")
                ),
                vol.Required(
                    CONF_RESERVED_SLOTS,
                    default=_format_reserved_slots(DEFAULT_RESERVED_SLOTS),
                ): str,
                vol.Required(CONF_AUTO_EXPIRE, default=DEFAULT_AUTO_EXPIRE): bool,
                vol.Required(CONF_CLEANUP_TIME, default=DEFAULT_CLEANUP_TIME): selector.TimeSelector(),
                vol.Required(
                    CONF_OVERWRITE_PROTECTION, default=DEFAULT_OVERWRITE_PROTECTION
                ): bool,
                vol.Required(CONF_PIN_LENGTH, default=str(DEFAULT_PIN_LENGTH)): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[str(length) for length in ALLOWED_PIN_LENGTHS],
                        mode=selector.SelectSelectorMode.LIST,
                        translation_key="pin_length",
                    )
                ),
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
        return NimlykoderOptionsFlow()


class NimlykoderOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Nimlykoder."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate slot range
            if user_input[CONF_SLOT_MIN] > user_input[CONF_SLOT_MAX]:
                errors["base"] = "invalid_slot_range"
            elif not _valid_base_topic(
                user_input.get(CONF_Z2M_BASE_TOPIC, DEFAULT_Z2M_BASE_TOPIC)
            ):
                errors["base"] = "invalid_z2m_base_topic"
            else:
                # Convert reserved_slots from string to list
                options = dict(user_input)
                options[CONF_Z2M_BASE_TOPIC] = user_input.get(
                    CONF_Z2M_BASE_TOPIC, DEFAULT_Z2M_BASE_TOPIC
                ).strip().strip("/")
                options[CONF_RESERVED_SLOTS] = _parse_reserved_slots(
                    user_input.get(CONF_RESERVED_SLOTS, "")
                )
                # Convert pin_length from string (selector) to int
                options[CONF_PIN_LENGTH] = int(user_input.get(CONF_PIN_LENGTH, DEFAULT_PIN_LENGTH))
                if options.get(CONF_PROTECT_SENSITIVE):
                    previous = self.config_entry.options
                    changed_target = (
                        previous.get(CONF_LOCK_ENTITY) != options[CONF_LOCK_ENTITY]
                        or previous.get(CONF_Z2M_BASE_TOPIC, DEFAULT_Z2M_BASE_TOPIC)
                        != options[CONF_Z2M_BASE_TOPIC]
                    )
                    if not previous.get(CONF_PROTECT_SENSITIVE) or changed_target:
                        self._pending_options = options
                        return await self.async_step_confirm_protection()
                    try:
                        restart_required = await self._apply_protection(options)
                    except (ValueError, Zigbee2MqttProtectionError) as err:
                        errors["base"] = (
                            err.code
                            if isinstance(err, Zigbee2MqttProtectionError)
                            else "protection_device_unavailable"
                        )
                    else:
                        if restart_required:
                            self._notify_restart_required()
                        return self.async_create_entry(title="", data=options)
                else:
                    return self.async_create_entry(title="", data=options)

        # Get current options with safe defaults
        options = self.config_entry.options or {}

        # Format reserved_slots for display
        current_reserved = options.get(CONF_RESERVED_SLOTS)
        if current_reserved is None:
            current_reserved = DEFAULT_RESERVED_SLOTS
        if isinstance(current_reserved, list):
            current_reserved = _format_reserved_slots(current_reserved)
        elif not isinstance(current_reserved, str):
            current_reserved = _format_reserved_slots(DEFAULT_RESERVED_SLOTS)

        # Get other options with safe defaults
        lock_entity = options.get(CONF_LOCK_ENTITY) or ""
        slot_min = options.get(CONF_SLOT_MIN)
        if slot_min is None:
            slot_min = DEFAULT_SLOT_MIN
        slot_max = options.get(CONF_SLOT_MAX)
        if slot_max is None:
            slot_max = DEFAULT_SLOT_MAX
        auto_expire = options.get(CONF_AUTO_EXPIRE)
        if auto_expire is None:
            auto_expire = DEFAULT_AUTO_EXPIRE
        cleanup_time = options.get(CONF_CLEANUP_TIME) or DEFAULT_CLEANUP_TIME
        overwrite_protection = options.get(CONF_OVERWRITE_PROTECTION)
        if overwrite_protection is None:
            overwrite_protection = DEFAULT_OVERWRITE_PROTECTION
        pin_length = options.get(CONF_PIN_LENGTH, DEFAULT_PIN_LENGTH)
        protect_sensitive = options.get(CONF_PROTECT_SENSITIVE, False)
        z2m_base_topic = options.get(CONF_Z2M_BASE_TOPIC) or _base_topic_for_lock(
            self.hass, lock_entity
        )

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOCK_ENTITY,
                    default=lock_entity,
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="lock")
                ),
                vol.Required(
                    CONF_SLOT_MIN,
                    default=slot_min,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=99, mode="box")
                ),
                vol.Required(
                    CONF_SLOT_MAX,
                    default=slot_max,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=99, mode="box")
                ),
                vol.Required(
                    CONF_RESERVED_SLOTS,
                    default=current_reserved,
                ): str,
                vol.Required(
                    CONF_AUTO_EXPIRE,
                    default=auto_expire,
                ): bool,
                vol.Required(
                    CONF_CLEANUP_TIME,
                    default=cleanup_time,
                ): selector.TimeSelector(),
                vol.Required(
                    CONF_OVERWRITE_PROTECTION,
                    default=overwrite_protection,
                ): bool,
                vol.Required(
                    CONF_PIN_LENGTH,
                    default=str(pin_length),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[str(length) for length in ALLOWED_PIN_LENGTHS],
                        mode=selector.SelectSelectorMode.LIST,
                        translation_key="pin_length",
                    )
                ),
                vol.Required(
                    CONF_PROTECT_SENSITIVE,
                    default=protect_sensitive,
                ): bool,
                vol.Required(
                    CONF_Z2M_BASE_TOPIC,
                    default=z2m_base_topic,
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )

    async def async_step_confirm_protection(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Require explicit consent before changing Zigbee2MQTT device options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get("confirm_protection"):
                errors["base"] = "protection_consent_required"
            else:
                options = self._pending_options
                try:
                    restart_required = await self._apply_protection(options)
                except (ValueError, Zigbee2MqttProtectionError) as err:
                    errors["base"] = (
                        err.code
                        if isinstance(err, Zigbee2MqttProtectionError)
                        else "protection_device_unavailable"
                    )
                else:
                    if restart_required:
                        self._notify_restart_required()
                    return self.async_create_entry(title="", data=options)

        return self.async_show_form(
            step_id="confirm_protection",
            data_schema=vol.Schema(
                {vol.Required("confirm_protection", default=False): bool}
            ),
            errors=errors,
        )

    async def _apply_protection(self, options: dict[str, Any]) -> bool:
        """Apply and verify protection for the explicitly selected lock."""
        device_id, resolved_base_topic = resolve_z2m_device(
            self.hass, options[CONF_LOCK_ENTITY]
        )
        adapter = MqttZ2mAdapter(
            self.hass,
            resolved_base_topic or options[CONF_Z2M_BASE_TOPIC],
        )
        return await adapter.async_enable_sensitive_protection(device_id)

    def _notify_restart_required(self) -> None:
        """Tell the user when Zigbee2MQTT requires a restart for the filters."""
        from homeassistant.components import persistent_notification

        if self.hass.config.language == "sv":
            message = (
                "Zigbee2MQTT rapporterade att ändringen kräver en omstart. "
                "Starta om Zigbee2MQTT för att skyddet ska börja gälla."
            )
            title = "Nimlykoder: omstart av Zigbee2MQTT krävs"
        else:
            message = (
                "Zigbee2MQTT reported that this change requires a restart. "
                "Restart Zigbee2MQTT for the protection to take effect."
            )
            title = "Nimlykoder: Zigbee2MQTT restart required"
        persistent_notification.async_create(
            self.hass,
            message,
            title=title,
            notification_id="nimlykoder_sensitive_protection_restart",
        )


def _base_topic_for_lock(hass: Any, entity_id: str) -> str:
    """Use the selected MQTT device's discovered base topic when available."""
    try:
        _, base_topic = resolve_z2m_device(hass, entity_id)
    except ValueError:
        return DEFAULT_Z2M_BASE_TOPIC
    return base_topic or DEFAULT_Z2M_BASE_TOPIC
