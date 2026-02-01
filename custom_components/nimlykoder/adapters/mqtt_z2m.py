"""MQTT adapter for Zigbee2MQTT communication with Nimly locks."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

# Set to True to enable actual MQTT communication
# Set to False for development/testing without MQTT
MQTT_ENABLED = False


class MqttZ2mAdapter:
    """Adapter for communicating with Nimly locks via Zigbee2MQTT."""

    def __init__(self, hass: HomeAssistant, base_topic: str) -> None:
        """Initialize the adapter."""
        self.hass = hass
        self.base_topic = base_topic.rstrip("/")

    async def add_code(self, slot: int, pin_code: str) -> None:
        """Add a PIN code to the lock.

        Args:
            slot: User slot number (0-99)
            pin_code: PIN code to set

        Raises:
            HomeAssistantError: If MQTT publish fails
        """
        topic = f"{self.base_topic}/set"
        payload = {
            "pin_code": {
                "user": slot,
                "user_enabled": True,
                "pin_code": pin_code,
            }
        }

        if not MQTT_ENABLED:
            _LOGGER.info("[DEV MODE] Would publish add code for slot %s to %s: %s", slot, topic, payload)
            return

        try:
            from homeassistant.components import mqtt
            await mqtt.async_publish(self.hass, topic, payload, qos=1, retain=False)
            _LOGGER.info("Published add code for slot %s to %s", slot, topic)
        except Exception as err:
            _LOGGER.error("Failed to publish add code to MQTT: %s", err)
            raise HomeAssistantError(f"Failed to add code via MQTT: {err}") from err

    async def remove_code(self, slot: int) -> None:
        """Remove a PIN code from the lock.

        Args:
            slot: User slot number to clear

        Raises:
            HomeAssistantError: If MQTT publish fails
        """
        topic = f"{self.base_topic}/set"
        payload = {
            "pin_code": {
                "user": slot,
                "user_enabled": False,
                "pin_code": None,
            }
        }

        if not MQTT_ENABLED:
            _LOGGER.info("[DEV MODE] Would publish remove code for slot %s to %s: %s", slot, topic, payload)
            return

        try:
            from homeassistant.components import mqtt
            await mqtt.async_publish(self.hass, topic, payload, qos=1, retain=False)
            _LOGGER.info("Published remove code for slot %s to %s", slot, topic)
        except Exception as err:
            _LOGGER.error("Failed to publish remove code to MQTT: %s", err)
            raise HomeAssistantError(
                f"Failed to remove code via MQTT: {err}"
            ) from err

    async def verify_connection(self) -> bool:
        """Verify MQTT connection is available.

        Returns:
            True if MQTT is available, False otherwise
        """
        if not MQTT_ENABLED:
            _LOGGER.info("[DEV MODE] MQTT disabled, skipping connection check")
            return True

        try:
            from homeassistant.components import mqtt
            # Check if MQTT integration is loaded
            return mqtt.DOMAIN in self.hass.config.components
        except Exception as err:
            _LOGGER.error("Failed to verify MQTT connection: %s", err)
            return False
