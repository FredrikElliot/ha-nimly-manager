"""Last lock/unlock attribution sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity

from .activity import EVENT_LOCK_ACTIVITY
from .const import CONF_LOCK_ENTITY, DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    """Create separate sensors so relocking preserves unlock attribution."""
    async_add_entities(
        [LockActivitySensor(hass.data[DOMAIN], entry, action) for action in ("lock", "unlock")]
    )


class LockActivitySensor(SensorEntity, RestoreEntity):
    """Display a name when known and an explicit fallback otherwise."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, data, entry, action):
        self._data = data
        self._entry_id = entry.entry_id
        self._action = action
        self._activity = None
        self._attr_unique_id = f"{entry.entry_id}_last_{action}ed_by"
        self._attr_translation_key = f"last_{action}ed_by"
        self._attr_icon = "mdi:lock-open" if action == "unlock" else "mdi:lock"

    async def async_added_to_hass(self):
        """Restore display state without emitting historical activity."""
        await super().async_added_to_hass()
        previous = await self.async_get_last_state()
        if previous is not None and previous.attributes.get("action") == self._action:
            self._activity = {
                key: previous.attributes.get(key)
                for key in ("action", "name", "method", "source", "slot", "timestamp")
            }

        @callback
        def activity_received(event):
            if (
                event.data.get("entry_id") == self._entry_id
                and event.data.get("action") == self._action
            ):
                self._activity = self._data["activity"].last[self._action]
                self.async_write_ha_state()

        self.async_on_remove(
            self.hass.bus.async_listen(EVENT_LOCK_ACTIVITY, activity_received)
        )
        if activity := self._data["activity"].last.get(self._action):
            self._activity = activity

    @property
    def native_value(self):
        if not self._activity:
            return None
        if self._activity.get("name"):
            return self._activity["name"]
        method = self._activity.get("method", "unknown")
        return "unknown_credential" if method in ("pin", "rfid", "fingerprint") else method

    @property
    def extra_state_attributes(self):
        return {
            "entity_id": self._data["config"].get(CONF_LOCK_ENTITY),
            **(self._activity or {}),
        }
