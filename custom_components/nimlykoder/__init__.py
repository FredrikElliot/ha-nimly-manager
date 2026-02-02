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
    """Derive MQTT topic from a lock entity ID."""
    # For Zigbee2MQTT, the entity ID format is typically: lock.device_name
    # The MQTT topic is typically: zigbee2mqtt/device_name
    
    # Get the entity registry entry to find the device
    ent_reg = er.async_get(hass)
    entry = ent_reg.async_get(entity_id)
    
    if entry and entry.unique_id:
        # Zigbee2MQTT unique IDs often contain the device friendly name
        # Format varies, but we can try to extract it
        unique_id = entry.unique_id
        
        # Common Z2M format: "0x00158d0001234567_lock" or just device name
        if "_" in unique_id:
            device_name = unique_id.rsplit("_", 1)[0]
        else:
            device_name = unique_id
            
        # If it looks like a Zigbee address, use the entity name instead
        if device_name.startswith("0x"):
            # Fall back to entity name
            device_name = entity_id.replace("lock.", "").replace("_", " ")
        
        return f"zigbee2mqtt/{device_name}"
    
    # Fallback: derive from entity_id
    device_name = entity_id.replace("lock.", "").replace("_", " ")
    return f"zigbee2mqtt/{device_name}"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Nimlykoder from a config entry."""
    # Get configuration
    options = entry.options
    
    # Support both new (lock_entity) and legacy (mqtt_topic) config
    lock_entity = options.get(CONF_LOCK_ENTITY)
    mqtt_topic = options.get(CONF_MQTT_TOPIC)
    
    if lock_entity:
        # New config: derive MQTT topic from entity
        mqtt_topic = _get_mqtt_topic_from_entity(hass, lock_entity)
        _LOGGER.debug("Derived MQTT topic '%s' from entity '%s'", mqtt_topic, lock_entity)
    elif not mqtt_topic:
        # No config at all - shouldn't happen but handle gracefully
        _LOGGER.error("No lock entity or MQTT topic configured")
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

    # Initialize storage
    storage = NimlykoderStorage(hass)
    await storage.async_load()

    # Initialize MQTT adapter
    mqtt_adapter = MqttZ2mAdapter(hass, config[CONF_MQTT_TOPIC])

    # Verify MQTT is available
    if not await mqtt_adapter.verify_connection():
        _LOGGER.warning("MQTT integration not loaded, functionality will be limited")

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
