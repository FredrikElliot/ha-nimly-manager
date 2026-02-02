"""Services for Nimlykoder integration."""
from __future__ import annotations

import logging
from datetime import datetime, date

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_ADD_CODE,
    SERVICE_REMOVE_CODE,
    SERVICE_UPDATE_EXPIRY,
    SERVICE_LIST_CODES,
    SERVICE_CLEANUP_EXPIRED,
    TYPE_PERMANENT,
    TYPE_GUEST,
)

_LOGGER = logging.getLogger(__name__)

# Service schemas
SERVICE_ADD_CODE_SCHEMA = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Required("pin_code"): cv.string,
        vol.Required("type"): vol.In([TYPE_PERMANENT, TYPE_GUEST]),
        vol.Optional("expiry"): cv.string,
        vol.Optional("slot"): cv.positive_int,
        vol.Optional("force", default=False): cv.boolean,
    }
)

SERVICE_REMOVE_CODE_SCHEMA = vol.Schema(
    {
        vol.Required("slot"): cv.positive_int,
    }
)

SERVICE_UPDATE_EXPIRY_SCHEMA = vol.Schema(
    {
        vol.Required("slot"): cv.positive_int,
        vol.Optional("expiry"): cv.string,
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Nimlykoder."""

    async def handle_add_code(call: ServiceCall) -> None:
        """Handle add_code service call."""
        data = hass.data[DOMAIN]
        storage = data["storage"]
        mqtt_adapter = data["mqtt_adapter"]
        config = data["config"]

        name = call.data["name"]
        pin_code = call.data["pin_code"]
        code_type = call.data["type"]
        expiry = call.data.get("expiry")
        preferred_slot = call.data.get("slot")
        force = call.data.get("force", False)

        # Validate PIN code is 6 digits
        if not pin_code.isdigit() or len(pin_code) != 6:
            raise HomeAssistantError("PIN code must be exactly 6 digits")

        # Policy enforcement
        if code_type == TYPE_GUEST and not expiry:
            raise HomeAssistantError("Guest codes must have an expiry date")

        # Validate expiry format if provided
        if expiry:
            try:
                datetime.fromisoformat(expiry)
            except ValueError as err:
                raise HomeAssistantError(f"Invalid expiry date format: {err}") from err

        # Determine slot
        if preferred_slot is not None:
            slot = preferred_slot
            # Check bounds
            if slot < config[
                "slot_min"
            ] or slot > config["slot_max"]:
                raise HomeAssistantError(
                    f"Slot {slot} outside configured range "
                    f"({config['slot_min']}-{config['slot_max']})"
                )
            # Check if occupied
            if storage.is_slot_occupied(slot):
                if not force and config.get("overwrite_protection", True):
                    raise HomeAssistantError(
                        f"Slot {slot} is occupied. Use force=true to overwrite"
                    )
        else:
            # Auto-select slot
            slot = storage.find_first_free_slot(
                config["slot_min"],
                config["slot_max"],
                config["reserved_slots"],
            )
            if slot is None:
                raise HomeAssistantError("No free slots available")

        # Check reserved slots
        if preferred_slot is None and slot in config["reserved_slots"]:
            raise HomeAssistantError(f"Slot {slot} is reserved")

        # Add to MQTT first
        try:
            await mqtt_adapter.add_code(slot, pin_code)
        except Exception as err:
            raise HomeAssistantError(f"Failed to add code via MQTT: {err}") from err

        # Then store
        try:
            await storage.add(slot, name, code_type, expiry)
            _LOGGER.info(
                "Added %s code '%s' to slot %s", code_type, name, slot
            )
        except Exception as err:
            # Try to clean up MQTT if storage fails
            try:
                await mqtt_adapter.remove_code(slot)
            except Exception:
                pass
            raise

    async def handle_remove_code(call: ServiceCall) -> None:
        """Handle remove_code service call."""
        data = hass.data[DOMAIN]
        storage = data["storage"]
        mqtt_adapter = data["mqtt_adapter"]

        slot = call.data["slot"]

        # Check if slot exists
        entry = storage.get(slot)
        if entry is None:
            raise HomeAssistantError(f"Slot {slot} not found")

        # Remove from MQTT
        try:
            await mqtt_adapter.remove_code(slot)
        except Exception as err:
            raise HomeAssistantError(f"Failed to remove code via MQTT: {err}") from err

        # Remove from storage
        await storage.remove(slot)
        _LOGGER.info("Removed code from slot %s", slot)

    async def handle_update_expiry(call: ServiceCall) -> None:
        """Handle update_expiry service call."""
        data = hass.data[DOMAIN]
        storage = data["storage"]

        slot = call.data["slot"]
        expiry = call.data.get("expiry")

        # Validate expiry format if provided
        if expiry:
            try:
                datetime.fromisoformat(expiry)
            except ValueError as err:
                raise HomeAssistantError(f"Invalid expiry date format: {err}") from err

        # Update storage
        try:
            await storage.update_expiry(slot, expiry)
            _LOGGER.info("Updated expiry for slot %s to %s", slot, expiry)
        except Exception as err:
            raise HomeAssistantError(f"Failed to update expiry: {err}") from err

    async def handle_list_codes(call: ServiceCall) -> None:
        """Handle list_codes service call."""
        data = hass.data[DOMAIN]
        storage = data["storage"]

        entries = storage.list_entries()
        _LOGGER.info("Listed %d codes", len(entries))

        # Return as service response
        return {"codes": [entry.to_dict() for entry in entries]}

    async def handle_cleanup_expired(call: ServiceCall) -> None:
        """Handle cleanup_expired service call - manually trigger expired code cleanup."""
        data = hass.data[DOMAIN]
        storage = data["storage"]
        mqtt_adapter = data["mqtt_adapter"]

        today = date.today()
        expired_slots = storage.expired_guest_slots(today)

        if not expired_slots:
            _LOGGER.info("No expired guest codes to clean up")
            return {"removed": 0, "slots": []}

        _LOGGER.info("Manually cleaning up %d expired guest codes", len(expired_slots))
        removed_slots = []

        for slot in expired_slots:
            try:
                entry = storage.get(slot)
                name = entry.name if entry else f"Slot {slot}"

                # Remove from MQTT/lock
                await mqtt_adapter.remove_code(slot)
                # Remove from storage
                await storage.remove(slot)

                _LOGGER.info("Removed expired code '%s' from slot %s", name, slot)
                removed_slots.append(slot)
            except Exception as err:
                _LOGGER.error("Failed to remove expired code from slot %s: %s", slot, err)

        _LOGGER.info("Manual cleanup completed: removed %d codes", len(removed_slots))
        return {"removed": len(removed_slots), "slots": removed_slots}

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_CODE,
        handle_add_code,
        schema=SERVICE_ADD_CODE_SCHEMA,
        supports_response=True,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_CODE,
        handle_remove_code,
        schema=SERVICE_REMOVE_CODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_EXPIRY,
        handle_update_expiry,
        schema=SERVICE_UPDATE_EXPIRY_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_CODES,
        handle_list_codes,
        supports_response=True,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEANUP_EXPIRED,
        handle_cleanup_expired,
        supports_response=True,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services."""
    hass.services.async_remove(DOMAIN, SERVICE_ADD_CODE)
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_CODE)
    hass.services.async_remove(DOMAIN, SERVICE_UPDATE_EXPIRY)
    hass.services.async_remove(DOMAIN, SERVICE_LIST_CODES)
    hass.services.async_remove(DOMAIN, SERVICE_CLEANUP_EXPIRED)
