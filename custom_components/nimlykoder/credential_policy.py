"""Credential management policy helpers."""


def is_reserved_pin_slot(slot: int, reserved_slots: list[int]) -> bool:
    """Return whether a PIN slot is a master or configured reserved slot."""
    return slot == 0 or slot in reserved_slots
