"""Storage management for Nimlykoder integration."""
from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, date
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CREDENTIAL_METHODS,
    CREDENTIAL_PIN,
    STORAGE_KEY,
    STORAGE_VERSION,
    TYPE_PERMANENT,
    TYPE_GUEST,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class CodeEntry:
    """Represents a lock credential."""

    slot: int
    name: str | None
    type: str
    expiry: str | None
    created: str
    updated: str
    method: str = CREDENTIAL_PIN
    discovered: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(slot: int, data: dict[str, Any]) -> CodeEntry:
        """Create from dictionary."""
        return CodeEntry(
            slot=slot,
            name=data["name"],
            type=data["type"],
            expiry=data.get("expiry"),
            created=data["created"],
            updated=data["updated"],
            method=data.get("method", CREDENTIAL_PIN),
            discovered=data.get("discovered", False),
        )


class NimlykoderStorage:
    """Manage persistent storage for PIN codes."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize storage."""
        self.hass = hass
        self._store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, dict[str, Any]] = {}

    async def async_load(self) -> None:
        """Load data from storage."""
        data = await self._store.async_load()
        if data is None:
            self._data = {}
        else:
            version = data.get("version", 1)
            if version == STORAGE_VERSION:
                self._data = data.get("entries", {})
            elif version == 1:
                self._data = {
                    self._key(CREDENTIAL_PIN, int(slot)): {
                        **entry,
                        "method": CREDENTIAL_PIN,
                        "discovered": False,
                    }
                    for slot, entry in data.get("entries", {}).items()
                }
                await self.async_save()
            else:
                _LOGGER.warning("Unknown storage version, resetting data")
                self._data = {}

    async def async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save(
            {
                "version": STORAGE_VERSION,
                "entries": self._data,
            }
        )

    def list_entries(self) -> list[CodeEntry]:
        """List all entries."""
        entries = []
        for key, data in self._data.items():
            method, slot = self._split_key(key, data)
            entries.append(CodeEntry.from_dict(slot, data | {"method": method}))
        return sorted(entries, key=lambda e: (e.method, e.slot))

    def get(self, slot: int, method: str = CREDENTIAL_PIN) -> CodeEntry | None:
        """Get entry by method and slot."""
        key = self._key(method, slot)
        if key not in self._data:
            return None
        return CodeEntry.from_dict(slot, self._data[key] | {"method": method})

    @staticmethod
    def _key(method: str, slot: int) -> str:
        """Return the storage key for a credential identity."""
        if method not in CREDENTIAL_METHODS:
            raise HomeAssistantError(f"Unknown credential method: {method}")
        return f"{method}:{slot}"

    @staticmethod
    def _split_key(key: str, data: dict[str, Any]) -> tuple[str, int]:
        """Read a current or legacy storage key."""
        if ":" in key:
            method, slot = key.split(":", 1)
            return method, int(slot)
        return data.get("method", CREDENTIAL_PIN), int(key)

    async def add(
        self,
        slot: int,
        name: str,
        code_type: str,
        expiry: str | None = None,
        method: str = CREDENTIAL_PIN,
    ) -> CodeEntry:
        """Add or replace an entry."""
        now = datetime.now().isoformat()
        key = self._key(method, slot)

        # Validate type and expiry
        if method == CREDENTIAL_PIN and code_type == TYPE_GUEST and expiry is None:
            raise HomeAssistantError("Guest codes must have an expiry date")

        entry_data = {
            "name": name,
            "type": code_type,
            "expiry": expiry,
            "created": now,
            "updated": now,
            "method": method,
            "discovered": False,
        }

        self._data[key] = entry_data
        await self.async_save()

        return CodeEntry.from_dict(slot, entry_data)

    async def discover(self, slot: int, method: str) -> CodeEntry:
        """Record a reported credential without replacing existing metadata."""
        key = self._key(method, slot)
        if key in self._data:
            return CodeEntry.from_dict(slot, self._data[key] | {"method": method})

        now = datetime.now().isoformat()
        entry_data = {
            "name": None,
            "type": TYPE_PERMANENT,
            "expiry": None,
            "created": now,
            "updated": now,
            "method": method,
            "discovered": True,
        }
        self._data[key] = entry_data
        await self.async_save()
        return CodeEntry.from_dict(slot, entry_data)

    async def remove(self, slot: int, method: str = CREDENTIAL_PIN) -> None:
        """Remove an entry by method and slot."""
        key = self._key(method, slot)
        if key in self._data:
            del self._data[key]
            await self.async_save()

    async def update_expiry(
        self, slot: int, expiry: str | None, method: str = CREDENTIAL_PIN
    ) -> CodeEntry:
        """Update expiry date."""
        key = self._key(method, slot)
        if method != CREDENTIAL_PIN:
            raise HomeAssistantError("Expiry dates are only supported for PIN codes")
        if key not in self._data:
            raise HomeAssistantError(f"Slot {slot} not found")

        self._data[key]["expiry"] = expiry
        self._data[key]["updated"] = datetime.now().isoformat()
        await self.async_save()

        return CodeEntry.from_dict(slot, self._data[key])

    async def update_name(
        self, slot: int, name: str, method: str = CREDENTIAL_PIN
    ) -> CodeEntry:
        """Update name for a credential entry."""
        key = self._key(method, slot)
        if key not in self._data:
            raise HomeAssistantError(f"Slot {slot} not found")

        if not name or not name.strip():
            raise HomeAssistantError("Name cannot be empty")

        self._data[key]["name"] = name.strip()
        self._data[key]["updated"] = datetime.now().isoformat()
        await self.async_save()

        return CodeEntry.from_dict(slot, self._data[key])

    def find_first_free_slot(
        self, slot_min: int, slot_max: int, reserved_slots: list[int]
    ) -> int | None:
        """Find first available slot outside reserved range."""
        for slot in range(slot_min, slot_max + 1):
            if slot in reserved_slots:
                continue
            if not self.is_slot_occupied(slot):
                return slot
        return None

    def expired_guest_slots(self, today: date) -> list[int]:
        """Get list of expired guest code slots."""
        expired = []
        for key, data in self._data.items():
            method, slot = self._split_key(key, data)
            if (
                method == CREDENTIAL_PIN
                and data["type"] == TYPE_GUEST
                and data.get("expiry")
            ):
                try:
                    expiry_date = datetime.fromisoformat(data["expiry"]).date()
                    if expiry_date < today:
                        expired.append(slot)
                except (ValueError, TypeError):
                    _LOGGER.error("Invalid expiry date for slot %s", slot)
        return expired

    def is_slot_occupied(self, slot: int, method: str = CREDENTIAL_PIN) -> bool:
        """Check whether a method-specific slot is occupied."""
        return self._key(method, slot) in self._data
