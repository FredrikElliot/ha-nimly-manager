"""Helpers for identifying credentials in Zigbee2MQTT operation reports."""
from __future__ import annotations

from typing import Any

from .const import CREDENTIAL_FINGERPRINT, CREDENTIAL_PIN, CREDENTIAL_TAG


_SOURCE_METHODS = {
    "keypad": CREDENTIAL_PIN,
    "rfid": CREDENTIAL_TAG,
    "fingerprintsensor": CREDENTIAL_FINGERPRINT,
}


def credential_from_operation(payload: dict[str, Any]) -> tuple[str, int] | None:
    """Return a credential identity only for an attributed lock operation."""
    state = payload.get("state")
    if not isinstance(state, str):
        return None

    action = state.lower()
    if action == "unlock":
        prefix = "last_unlock"
    elif action == "lock":
        prefix = "last_lock"
    else:
        return None

    source = payload.get(f"{prefix}_source")
    method = _SOURCE_METHODS.get(source.lower()) if isinstance(source, str) else None
    slot = payload.get(f"{prefix}_user")
    if method is None or isinstance(slot, bool):
        return None

    if isinstance(slot, str) and slot.isdecimal():
        slot = int(slot)
    if not isinstance(slot, int) or not 0 <= slot <= 999:
        return None

    return method, slot
