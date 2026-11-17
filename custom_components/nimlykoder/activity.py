"""Normalize live Nimly operation reports without copying credential secrets."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


EVENT_LOCK_ACTIVITY = "nimlykoder_lock_activity"

SOURCE_METHODS = {
    "keypad": "pin",
    "rfid": "rfid",
    "fingerprintsensor": "fingerprint",
    "zigbee": "remote",
    "self": "automatic",
    "manual": "manual",
    "unattributed": "unattributed",
    "unknown": "unknown",
}


def _report_time(value: Any) -> datetime | None:
    """Read Zigbee2MQTT last_seen (ISO 8601, epoch or epoch_ms)."""
    try:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            seconds = value / 1000 if value > 100_000_000_000 else value
            return datetime.fromtimestamp(seconds, timezone.utc)
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError, OSError):
        pass
    return None


def _slot(value: Any) -> int | None:
    """Accept only a reported 16-bit user slot, never a credential value."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str) and len(value) <= 5 and value.isascii() and value.isdecimal():
        value = int(value)
    if isinstance(value, int) and 0 <= value < 65535:
        return value
    return None


class LockActivity:
    """Track operations, independently for locking and unlocking."""

    def __init__(self, storage: Any, started: datetime | None = None) -> None:
        self.storage = storage
        self.started = started or datetime.now(timezone.utc)
        self.last: dict[str, dict[str, Any]] = {}
        self._latest: datetime | None = None
        self._seen: set[tuple[str, str, int | None]] = set()

    def process(
        self, payload: Any, *, retained: bool = False
    ) -> dict[str, Any] | None:
        """Return a safe activity only for a new, timestamped operation."""
        if retained or not isinstance(payload, dict):
            return None
        action = payload.get("action")
        # last_* fields and lock state are cached state, not operation reports.
        if action not in ("lock", "unlock") or "action_source_name" not in payload:
            return None
        timestamp = _report_time(payload.get("last_seen"))
        if timestamp is None or timestamp <= self.started:
            return None
        if self._latest is not None and timestamp < self._latest:
            return None

        source = payload["action_source_name"]
        if not isinstance(source, str) or source not in SOURCE_METHODS:
            source = "unknown"
        method = SOURCE_METHODS[source]
        slot = _slot(payload.get("action_user"))
        identity = (action, source, slot)
        if timestamp == self._latest and identity in self._seen:
            return None
        if timestamp != self._latest:
            self._seen.clear()
        self._latest = timestamp
        self._seen.add(identity)

        # A zero slot is valid for credential sources, but does not identify a
        # person for self/zigbee/unattributed reports (including model source 05).
        name = None
        if method in ("pin", "rfid", "fingerprint") and slot is not None:
            name = self.storage.get_credential_name(method, slot)
        activity = {
            "action": action,
            "name": name,
            "method": method,
            "source": source,
            "slot": slot,
            "timestamp": timestamp.isoformat(),
        }
        self.last[action] = activity
        return activity
