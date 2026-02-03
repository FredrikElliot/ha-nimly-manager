"""The Nimlykoder integration."""
from __future__ import annotations

import logging
from datetime import date, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers import entity_registry as er
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    DOMAIN,
    CONF_LOCK_ENTITY,
    CONF_MQTT_TOPIC,
    CONF_SLOT_MIN,
    CONF_SLOT_MAX,
    CONF_RESERVED_SLOTS,
    CONF_AUTO_EXPIRE,
    CONF_CLEANUP_TIME,
    CONF_OVERWRITE_PROTECTION,
    DEFAULT_SLOT_MIN,
    DEFAULT_SLOT_MAX,
    DEFAULT_RESERVED_SLOTS,
    DEFAULT_AUTO_EXPIRE,
    DEFAULT_CLEANUP_TIME,
    DEFAULT_OVERWRITE_PROTECTION,
)
from .storage import NimlykoderStorage
from .adapters.mqtt_z2m import MqttZ2mAdapter
from .services import async_setup_services, async_unload_services
from .websocket import async_register_websocket_handlers
from .panel import async_register_panel, async_unregister_panel

_LOGGER = logging.getLogger(__name__)


def _get_mqtt_topic_from_entity(hass: HomeAssistant, entity_id: str) -> str | None:
    """Derive MQTT topic from a lock entity ID.
    
    For Zigbee2MQTT entities, we try to find the device's friendly name
    and construct the MQTT topic as: zigbee2mqtt/{friendly_name}
    """
    _LOGGER.info("[_get_mqtt_topic_from_entity] Deriving MQTT topic for entity: %s", entity_id)
    
    # Get the entity registry entry to find the device
    ent_reg = er.async_get(hass)
    entry = ent_reg.async_get(entity_id)
    
    if not entry:
        _LOGGER.warning(
            "[_get_mqtt_topic_from_entity] Entity '%s' not found in registry", entity_id
        )
        # Fallback: derive from entity_id
        device_name = entity_id.replace("lock.", "").replace("_", " ")
        mqtt_topic = f"zigbee2mqtt/{device_name}"
        _LOGGER.info(
            "[_get_mqtt_topic_from_entity] Using fallback topic from entity_id: %s",
            mqtt_topic,
        )
        return mqtt_topic
    
    _LOGGER.debug(
        "[_get_mqtt_topic_from_entity] Entity registry entry found: unique_id=%s, platform=%s, device_id=%s",
        entry.unique_id,
        entry.platform,
        entry.device_id,
    )
    
    # Try to get device info for better topic derivation
    if entry.device_id:
        from homeassistant.helpers import device_registry as dr
        dev_reg = dr.async_get(hass)
        device = dev_reg.async_get(entry.device_id)
        
        if device:
            _LOGGER.debug(
                "[_get_mqtt_topic_from_entity] Device found: name=%s, name_by_user=%s, identifiers=%s",
                device.name,
                device.name_by_user,
                device.identifiers,
            )
            
            # For Z2M devices, the identifier often contains the friendly name
            # Format: {("mqtt", "zigbee2mqtt_0x00158d0001234567")} or similar
            for domain, identifier in device.identifiers:
                _LOGGER.debug(
                    "[_get_mqtt_topic_from_entity] Checking identifier: domain=%s, id=%s",
                    domain,
                    identifier,
                )
                if domain == "mqtt" and identifier.startswith("zigbee2mqtt_"):
                    # Extract the device name from the identifier
                    device_name = identifier.replace("zigbee2mqtt_", "")
                    mqtt_topic = f"zigbee2mqtt/{device_name}"
                    _LOGGER.info(
                        "[_get_mqtt_topic_from_entity] Derived topic from device identifier: %s",
                        mqtt_topic,
                    )
                    return mqtt_topic
            
            # If device has a name, use that
            if device.name:
                mqtt_topic = f"zigbee2mqtt/{device.name}"
                _LOGGER.info(
                    "[_get_mqtt_topic_from_entity] Derived topic from device name: %s",
                    mqtt_topic,
                )
                return mqtt_topic
    
    # Try to extract from unique_id
    if entry.unique_id:
        unique_id = entry.unique_id
        _LOGGER.debug(
            "[_get_mqtt_topic_from_entity] Trying to derive from unique_id: %s", unique_id
        )
        
        # Common Z2M format: "0x00158d0001234567_lock" or "friendly_name_lock"
        if "_" in unique_id:
            device_name = unique_id.rsplit("_", 1)[0]
        else:
            device_name = unique_id
            
        # If it looks like a Zigbee address, we can't derive a meaningful name
        if device_name.startswith("0x"):
            _LOGGER.warning(
                "[_get_mqtt_topic_from_entity] unique_id appears to be a Zigbee address. "
                "Using entity name as fallback."
            )
            device_name = entity_id.replace("lock.", "").replace("_", " ")
        
        mqtt_topic = f"zigbee2mqtt/{device_name}"
        _LOGGER.info(
            "[_get_mqtt_topic_from_entity] Derived topic from unique_id: %s", mqtt_topic
        )
        return mqtt_topic
    
    # Final fallback: derive from entity_id
    device_name = entity_id.replace("lock.", "").replace("_", " ")
    mqtt_topic = f"zigbee2mqtt/{device_name}"
    _LOGGER.warning(
        "[_get_mqtt_topic_from_entity] Using final fallback topic: %s", mqtt_topic
    )
    return mqtt_topic


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nimlykoder from a config entry."""
    _LOGGER.info("[async_setup_entry] Starting Nimlykoder setup...")
    
    # Get configuration
    options = entry.options
    _LOGGER.debug("[async_setup_entry] Config options: %s", options)
    
    # Support both new (lock_entity) and legacy (mqtt_topic) config
    lock_entity = options.get(CONF_LOCK_ENTITY)
    mqtt_topic = options.get(CONF_MQTT_TOPIC)
    
    _LOGGER.info(
        "[async_setup_entry] Config - lock_entity=%s, legacy_mqtt_topic=%s",
        lock_entity,
        mqtt_topic,
    )
    
    if lock_entity:
        # New config: derive MQTT topic from entity
        _LOGGER.info("[async_setup_entry] Using entity selector config")
        mqtt_topic = _get_mqtt_topic_from_entity(hass, lock_entity)
        if not mqtt_topic:
            _LOGGER.error(
                "[async_setup_entry] Failed to derive MQTT topic from entity '%s'",
                lock_entity,
            )
            return False
        _LOGGER.info(
            "[async_setup_entry] Derived MQTT topic '%s' from entity '%s'",
            mqtt_topic,
            lock_entity,
        )
    elif mqtt_topic:
        _LOGGER.info(
            "[async_setup_entry] Using legacy MQTT topic config: %s", mqtt_topic
        )
    else:
        # No config at all - shouldn't happen but handle gracefully
        _LOGGER.error("[async_setup_entry] No lock entity or MQTT topic configured!")
        return False
    
    # Ensure slot values are integers
    slot_min = options.get(CONF_SLOT_MIN, DEFAULT_SLOT_MIN)
    slot_max = options.get(CONF_SLOT_MAX, DEFAULT_SLOT_MAX)
    if isinstance(slot_min, float):
        slot_min = int(slot_min)
    if isinstance(slot_max, float):
        slot_max = int(slot_max)
    
    config = {
        CONF_LOCK_ENTITY: lock_entity,
        CONF_MQTT_TOPIC: mqtt_topic,
        CONF_SLOT_MIN: slot_min,
        CONF_SLOT_MAX: slot_max,
        CONF_RESERVED_SLOTS: options.get(CONF_RESERVED_SLOTS, DEFAULT_RESERVED_SLOTS),
        CONF_AUTO_EXPIRE: options.get(CONF_AUTO_EXPIRE, DEFAULT_AUTO_EXPIRE),
        CONF_CLEANUP_TIME: options.get(CONF_CLEANUP_TIME, DEFAULT_CLEANUP_TIME),
        CONF_OVERWRITE_PROTECTION: options.get(
            CONF_OVERWRITE_PROTECTION, DEFAULT_OVERWRITE_PROTECTION
        ),
    }
    
    _LOGGER.info(
        "[async_setup_entry] Final config - mqtt_topic=%s, slots=%d-%d, auto_expire=%s",
        config[CONF_MQTT_TOPIC],
        config[CONF_SLOT_MIN],
        config[CONF_SLOT_MAX],
        config[CONF_AUTO_EXPIRE],
    )

    # Initialize storage
    _LOGGER.debug("[async_setup_entry] Initializing storage...")
    storage = NimlykoderStorage(hass)
    await storage.async_load()
    _LOGGER.info("[async_setup_entry] Storage loaded with %d entries", len(storage.list_entries()))

    # Initialize MQTT adapter
    _LOGGER.debug("[async_setup_entry] Initializing MQTT adapter...")
    mqtt_adapter = MqttZ2mAdapter(hass, config[CONF_MQTT_TOPIC])

    # Verify MQTT is available
    mqtt_available = await mqtt_adapter.verify_connection()
    if not mqtt_available:
        _LOGGER.warning(
            "[async_setup_entry] MQTT integration not loaded! "
            "PIN codes will NOT be sent to the lock. "
            "Please configure MQTT in Home Assistant."
        )
    else:
        _LOGGER.info("[async_setup_entry] MQTT connection verified successfully")

    # Store data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN] = {
        "storage": storage,
        "mqtt_adapter": mqtt_adapter,
        "config": config,
        "entry": entry,
        "cleanup_unsub": None,
    }

    # Register services
    _LOGGER.debug("[async_setup_entry] Registering services...")
    await async_setup_services(hass)

    # Register WebSocket handlers
    async_register_websocket_handlers(hass)

    # Register panel
    await async_register_panel(hass)

    # Set up scheduler for expired code cleanup
    if config[CONF_AUTO_EXPIRE]:
        unsub = await async_setup_cleanup_scheduler(hass, config[CONF_CLEANUP_TIME])
        hass.data[DOMAIN]["cleanup_unsub"] = unsub

    # Listen for options updates
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    _LOGGER.info("Nimlykoder integration set up successfully")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Cancel cleanup scheduler
    data = hass.data.get(DOMAIN)
    if data and data.get("cleanup_unsub"):
        data["cleanup_unsub"]()

    # Unregister services
    await async_unload_services(hass)

    # Unregister panel
    await async_unregister_panel(hass)

    # Clean up data
    hass.data.pop(DOMAIN, None)

    _LOGGER.info("Nimlykoder integration unloaded")
    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_cleanup_scheduler(hass: HomeAssistant, cleanup_time: str):
    """Set up daily cleanup scheduler. Returns unsub function."""
    try:
        # Parse cleanup time (format: HH:MM:SS)
        time_parts = cleanup_time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        second = int(time_parts[2]) if len(time_parts) > 2 else 0

        @callback
        def cleanup_expired_codes(now):
            """Clean up expired guest codes."""
            hass.async_create_task(_async_cleanup_expired_codes(hass))

        # Schedule daily cleanup
        unsub = async_track_time_change(
            hass, cleanup_expired_codes, hour=hour, minute=minute, second=second
        )

        _LOGGER.info(
            "Scheduled daily expired code cleanup at %02d:%02d:%02d",
            hour, minute, second
        )
        return unsub

    except Exception as err:
        _LOGGER.error("Failed to set up cleanup scheduler: %s", err)
        return None


async def _async_cleanup_expired_codes(hass: HomeAssistant) -> None:
    """Clean up expired guest codes."""
    try:
        data = hass.data.get(DOMAIN)
        if not data:
            _LOGGER.warning("Nimlykoder data not available for cleanup")
            return

        config = data["config"]
        if not config.get(CONF_AUTO_EXPIRE, True):
            _LOGGER.debug("Auto-expire is disabled, skipping cleanup")
            return

        storage = data["storage"]
        mqtt_adapter = data["mqtt_adapter"]

        today = date.today()
        expired_slots = storage.expired_guest_slots(today)

        if not expired_slots:
            _LOGGER.debug("No expired guest codes to clean up")
            return

        _LOGGER.info("Starting cleanup of %d expired guest codes", len(expired_slots))
        removed_count = 0

        for slot in expired_slots:
            try:
                entry = storage.get(slot)
                name = entry.name if entry else f"Slot {slot}"
                
                # Remove from MQTT/lock
                await mqtt_adapter.remove_code(slot)
                # Remove from storage
                await storage.remove(slot)
                
                _LOGGER.info(
                    "Removed expired code '%s' from slot %s", name, slot
                )
                removed_count += 1
            except Exception as err:
                _LOGGER.error(
                    "Failed to remove expired code from slot %s: %s", slot, err
                )

        _LOGGER.info(
            "Cleanup completed: removed %d of %d expired codes",
            removed_count, len(expired_slots)
        )

    except Exception as err:
        _LOGGER.error("Error during cleanup: %s", err)
