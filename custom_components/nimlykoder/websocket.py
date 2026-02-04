"""WebSocket API for Nimlykoder integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    WS_TYPE_LIST,
    WS_TYPE_ADD,
    WS_TYPE_REMOVE,
    WS_TYPE_UPDATE_EXPIRY,
    WS_TYPE_UPDATE_NAME,
    WS_TYPE_UPDATE_PIN,
    WS_TYPE_SUGGEST_SLOTS,
    WS_TYPE_CONFIG,
    WS_TYPE_TRANSLATIONS,
    TYPE_PERMANENT,
    TYPE_GUEST,
    CONF_AUTO_EXPIRE,
    CONF_CLEANUP_TIME,
)

_LOGGER = logging.getLogger(__name__)


@callback
def async_register_websocket_handlers(hass: HomeAssistant) -> None:
    """Register WebSocket handlers."""
    websocket_api.async_register_command(hass, handle_list)
    websocket_api.async_register_command(hass, handle_add)
    websocket_api.async_register_command(hass, handle_remove)
    websocket_api.async_register_command(hass, handle_update_expiry)
    websocket_api.async_register_command(hass, handle_update_name)
    websocket_api.async_register_command(hass, handle_update_pin)
    websocket_api.async_register_command(hass, handle_suggest_slots)
    websocket_api.async_register_command(hass, handle_config)
    websocket_api.async_register_command(hass, handle_translations)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_LIST,
    }
)
@websocket_api.async_response
async def handle_list(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle list command."""
    try:
        data = hass.data[DOMAIN]
        storage = data["storage"]

        entries = storage.list_entries()
        connection.send_result(
            msg["id"],
            {"codes": [entry.to_dict() for entry in entries]},
        )
    except Exception as err:
        _LOGGER.error("Error listing codes: %s", err)
        connection.send_error(msg["id"], "list_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_ADD,
        vol.Required("name"): str,
        vol.Required("pin_code"): str,
        vol.Required("code_type"): vol.In([TYPE_PERMANENT, TYPE_GUEST]),
        vol.Optional("expiry"): str,
        vol.Optional("slot"): int,
        vol.Optional("force", default=False): bool,
    }
)
@websocket_api.async_response
async def handle_add(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle add command."""
    try:
        data = hass.data[DOMAIN]
        storage = data["storage"]
        mqtt_adapter = data["mqtt_adapter"]
        config = data["config"]

        name = msg["name"]
        pin_code = msg["pin_code"]
        code_type = msg["code_type"]
        expiry = msg.get("expiry")
        preferred_slot = msg.get("slot")
        force = msg.get("force", False)

        # Validate PIN code is 6 digits
        if not pin_code.isdigit() or len(pin_code) != 6:
            connection.send_error(
                msg["id"], "invalid_input", "PIN code must be exactly 6 digits"
            )
            return

        # Policy enforcement
        if code_type == TYPE_GUEST and not expiry:
            connection.send_error(
                msg["id"], "invalid_input", "Guest codes must have an expiry date"
            )
            return

        # Validate expiry format if provided
        if expiry:
            try:
                datetime.fromisoformat(expiry)
            except ValueError as err:
                connection.send_error(
                    msg["id"], "invalid_input", f"Invalid expiry date format: {err}"
                )
                return

        # Determine slot
        if preferred_slot is not None:
            slot = preferred_slot
            # Check bounds
            if slot < config["slot_min"] or slot > config["slot_max"]:
                connection.send_error(
                    msg["id"],
                    "invalid_slot",
                    f"Slot {slot} outside configured range",
                )
                return
            # Check if occupied
            if storage.is_slot_occupied(slot):
                if not force and config.get("overwrite_protection", True):
                    connection.send_error(
                        msg["id"],
                        "slot_occupied",
                        f"Slot {slot} is occupied. Use force to overwrite",
                    )
                    return
        else:
            # Auto-select slot
            slot = storage.find_first_free_slot(
                config["slot_min"],
                config["slot_max"],
                config["reserved_slots"],
            )
            if slot is None:
                connection.send_error(
                    msg["id"], "no_free_slots", "No free slots available"
                )
                return

        # Check reserved slots for auto-assignment
        if preferred_slot is None and slot in config["reserved_slots"]:
            connection.send_error(
                msg["id"], "slot_reserved", f"Slot {slot} is reserved"
            )
            return

        # Add to MQTT first
        try:
            await mqtt_adapter.add_code(slot, pin_code)
        except Exception as err:
            connection.send_error(
                msg["id"], "mqtt_error", f"Failed to add code via MQTT: {err}"
            )
            return

        # Then store
        try:
            entry = await storage.add(slot, name, code_type, expiry)
            _LOGGER.info("Added %s code '%s' to slot %s", code_type, name, slot)
            connection.send_result(msg["id"], {"entry": entry.to_dict()})
        except Exception as err:
            # Try to clean up MQTT if storage fails
            try:
                await mqtt_adapter.remove_code(slot)
            except Exception:
                pass
            connection.send_error(msg["id"], "storage_error", str(err))

    except Exception as err:
        _LOGGER.error("Error adding code: %s", err)
        connection.send_error(msg["id"], "add_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_REMOVE,
        vol.Required("slot"): int,
    }
)
@websocket_api.async_response
async def handle_remove(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle remove command."""
    try:
        data = hass.data[DOMAIN]
        storage = data["storage"]
        mqtt_adapter = data["mqtt_adapter"]

        slot = msg["slot"]

        # Check if slot exists
        entry = storage.get(slot)
        if entry is None:
            connection.send_error(msg["id"], "not_found", f"Slot {slot} not found")
            return

        # Remove from MQTT
        try:
            await mqtt_adapter.remove_code(slot)
        except Exception as err:
            connection.send_error(
                msg["id"], "mqtt_error", f"Failed to remove code via MQTT: {err}"
            )
            return

        # Remove from storage
        await storage.remove(slot)
        _LOGGER.info("Removed code from slot %s", slot)
        connection.send_result(msg["id"], {"success": True})

    except Exception as err:
        _LOGGER.error("Error removing code: %s", err)
        connection.send_error(msg["id"], "remove_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_UPDATE_EXPIRY,
        vol.Required("slot"): int,
        vol.Optional("expiry"): str,
    }
)
@websocket_api.async_response
async def handle_update_expiry(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_expiry command."""
    try:
        data = hass.data[DOMAIN]
        storage = data["storage"]

        slot = msg["slot"]
        expiry = msg.get("expiry")

        # Validate expiry format if provided
        if expiry:
            try:
                datetime.fromisoformat(expiry)
            except ValueError as err:
                connection.send_error(
                    msg["id"], "invalid_input", f"Invalid expiry date format: {err}"
                )
                return

        # Update storage
        try:
            entry = await storage.update_expiry(slot, expiry)
            _LOGGER.info("Updated expiry for slot %s to %s", slot, expiry)
            connection.send_result(msg["id"], {"entry": entry.to_dict()})
        except Exception as err:
            connection.send_error(msg["id"], "update_failed", str(err))

    except Exception as err:
        _LOGGER.error("Error updating expiry: %s", err)
        connection.send_error(msg["id"], "update_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_UPDATE_NAME,
        vol.Required("slot"): int,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def handle_update_name(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_name command."""
    try:
        data = hass.data[DOMAIN]
        storage = data["storage"]

        slot = msg["slot"]
        name = msg["name"]

        if not name or not name.strip():
            connection.send_error(msg["id"], "invalid_input", "Name cannot be empty")
            return

        # Check if slot exists
        entry = storage.get(slot)
        if entry is None:
            connection.send_error(msg["id"], "not_found", f"Slot {slot} not found")
            return

        # Update storage
        try:
            entry = await storage.update_name(slot, name)
            _LOGGER.info("Updated name for slot %s to '%s'", slot, name)
            connection.send_result(msg["id"], {"entry": entry.to_dict()})
        except Exception as err:
            connection.send_error(msg["id"], "update_failed", str(err))

    except Exception as err:
        _LOGGER.error("Error updating name: %s", err)
        connection.send_error(msg["id"], "update_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_UPDATE_PIN,
        vol.Required("slot"): int,
        vol.Required("pin_code"): str,
    }
)
@websocket_api.async_response
async def handle_update_pin(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_pin command - update PIN code for existing slot."""
    try:
        data = hass.data[DOMAIN]
        storage = data["storage"]
        mqtt_adapter = data["mqtt_adapter"]

        slot = msg["slot"]
        pin_code = msg["pin_code"]

        # Check if slot exists
        entry = storage.get(slot)
        if entry is None:
            connection.send_error(msg["id"], "not_found", f"Slot {slot} not found")
            return

        # Validate PIN code is 6 digits
        if not pin_code.isdigit() or len(pin_code) != 6:
            connection.send_error(
                msg["id"], "invalid_input", "PIN code must be exactly 6 digits"
            )
            return

        # Send new PIN to lock via MQTT
        _LOGGER.info("Updating PIN for slot %s via MQTT", slot)
        try:
            await mqtt_adapter.add_code(slot, pin_code)
        except Exception as err:
            connection.send_error(
                msg["id"], "mqtt_error", f"Failed to update PIN via MQTT: {err}"
            )
            return

        # Update the 'updated' timestamp in storage
        try:
            entry = await storage.update_name(slot, entry.name)  # This updates the timestamp
        except Exception as err:
            _LOGGER.warning("Failed to update timestamp: %s", err)

        _LOGGER.info("Successfully updated PIN for slot %s", slot)
        connection.send_result(msg["id"], {"success": True, "entry": entry.to_dict()})

    except Exception as err:
        _LOGGER.error("Error updating PIN: %s", err)
        connection.send_error(msg["id"], "update_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_SUGGEST_SLOTS,
        vol.Optional("count", default=5): int,
    }
)
@websocket_api.async_response
async def handle_suggest_slots(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle suggest_slots command."""
    try:
        data = hass.data[DOMAIN]
        storage = data["storage"]
        config = data["config"]

        count = msg.get("count", 5)
        suggestions = []

        for slot in range(config["slot_min"], config["slot_max"] + 1):
            if len(suggestions) >= count:
                break
            if slot in config["reserved_slots"]:
                continue
            if not storage.is_slot_occupied(slot):
                suggestions.append(slot)

        connection.send_result(msg["id"], {"slots": suggestions})

    except Exception as err:
        _LOGGER.error("Error suggesting slots: %s", err)
        connection.send_error(msg["id"], "suggest_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_CONFIG,
    }
)
@websocket_api.async_response
async def handle_config(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle config command - returns current configuration."""
    try:
        data = hass.data[DOMAIN]
        config = data["config"]

        connection.send_result(
            msg["id"],
            {
                "auto_expire": config.get(CONF_AUTO_EXPIRE, True),
                "cleanup_time": config.get(CONF_CLEANUP_TIME, "03:00:00"),
            },
        )

    except Exception as err:
        _LOGGER.error("Error getting config: %s", err)
        connection.send_error(msg["id"], "config_failed", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_TRANSLATIONS,
    }
)
@websocket_api.async_response
async def handle_translations(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle translations command - returns panel translations for current language."""
    import json
    from pathlib import Path

    try:
        # Get user's language from hass config
        language = hass.config.language or "en"

        # Path to translations directory
        translations_dir = Path(__file__).parent / "translations"

        # Try to load the user's language, fallback to English
        translation_file = translations_dir / f"{language}.json"

        def _load_translations() -> dict:
            """Load translations from file (runs in executor to avoid blocking)."""
            file_to_load = translation_file
            if not file_to_load.exists():
                file_to_load = translations_dir / "en.json"
            with open(file_to_load, "r", encoding="utf-8") as f:
                return json.load(f)

        # Run file I/O in executor to avoid blocking the event loop
        translations = await hass.async_add_executor_job(_load_translations)

        # Extract panel translations
        panel_translations = translations.get("panel", {})

        connection.send_result(
            msg["id"],
            {
                "language": language,
                "translations": panel_translations,
            },
        )

    except Exception as err:
        _LOGGER.error("Error getting translations: %s", err)
        connection.send_error(msg["id"], "translations_failed", str(err))
