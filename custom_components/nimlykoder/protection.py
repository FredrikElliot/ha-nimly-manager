"""Helpers for identifying the Zigbee2MQTT device selected by the user."""
from __future__ import annotations

import re

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

_IEEE_ADDRESS = re.compile(r"0x[0-9a-fA-F]{16}")


def resolve_z2m_device(
    hass: HomeAssistant, entity_id: str
) -> tuple[str, str | None]:
    """Resolve the selected lock to its stable IEEE address and MQTT base topic."""
    entity = er.async_get(hass).async_get(entity_id)
    if entity is None or entity.device_id is None:
        raise ValueError("The selected lock has no Zigbee2MQTT device entry.")

    device = dr.async_get(hass).async_get(entity.device_id)
    if device is None:
        raise ValueError("The selected lock device could not be found.")

    candidates = [
        (identifier, True)
        for domain, identifier in device.identifiers
        if domain == "mqtt"
    ]
    candidates.append((entity.unique_id, False))
    for candidate, is_mqtt_identifier in candidates:
        match = _IEEE_ADDRESS.search(candidate)
        if match:
            base_topic = candidate[: match.start()] if is_mqtt_identifier else None
            if base_topic and base_topic.endswith("_"):
                base_topic = base_topic[:-1]
            return match.group(0).lower(), base_topic or None

    raise ValueError("The selected lock has no stable Zigbee IEEE address.")


def resolve_z2m_device_id(hass: HomeAssistant, entity_id: str) -> str:
    """Resolve the selected lock to its stable Zigbee IEEE address."""
    return resolve_z2m_device(hass, entity_id)[0]
