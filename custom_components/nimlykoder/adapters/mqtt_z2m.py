"""MQTT adapter for Zigbee2MQTT communication with Nimly locks."""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from ..credential_events import credential_from_operation

if TYPE_CHECKING:
    from ..storage import NimlykoderStorage

_LOGGER = logging.getLogger(__name__)

# Set to True to enable actual MQTT communication
# Set to False for development/testing without MQTT
MQTT_ENABLED = True


class MqttZ2mAdapter:
    """Adapter for communicating with Nimly locks via Zigbee2MQTT."""

    def __init__(self, hass: HomeAssistant, base_topic: str) -> None:
        """Initialize the adapter."""
        self.hass = hass
        self.base_topic = base_topic.rstrip("/")
        _LOGGER.info(
            "[MqttZ2mAdapter] Initialized with base_topic='%s', MQTT_ENABLED=%s",
            self.base_topic,
            MQTT_ENABLED,
        )

    async def add_code(self, slot: int, pin_code: str, user_type: str = "unrestricted") -> None:
        """Add a PIN code to the lock.

        Args:
            slot: User slot number (0-99)
            pin_code: PIN code to set
            user_type: Type of user - unrestricted (default/owner), year_day_schedule,
                       week_day_schedule, master, or non_access

        Raises:
            HomeAssistantError: If MQTT publish fails
        """
        topic = f"{self.base_topic}/set"
        
        # Nimly documentation: https://www.zigbee2mqtt.io/devices/Nimly.html
        # pin_code composite: {"user": VALUE, "user_type": VALUE, "user_enabled": VALUE, "pin_code": VALUE}
        payload = {
            "pin_code": {
                "user": slot,
                "user_type": user_type,
                "user_enabled": True,
                "pin_code": int(pin_code),  # Documentation says pin_code is numeric
            }
        }

        _LOGGER.info(
            "[MqttZ2mAdapter] add_code() called - slot=%d, pin_code=%s (masked), user_type=%s, topic='%s'",
            slot,
            "*" * len(pin_code),
            user_type,
            topic,
        )
        if not MQTT_ENABLED:
            _LOGGER.warning(
                "[MqttZ2mAdapter] DEV MODE - MQTT disabled. Would publish to '%s': %s",
                topic,
                json.dumps(payload),
            )
            return

        try:
            from homeassistant.components import mqtt

            # Check if MQTT is available
            if mqtt.DOMAIN not in self.hass.config.components:
                _LOGGER.error(
                    "[MqttZ2mAdapter] MQTT integration not loaded! Cannot publish."
                )
                raise HomeAssistantError(
                    "MQTT integration not loaded. Please configure MQTT in Home Assistant."
                )

            _LOGGER.debug(
                "[MqttZ2mAdapter] Publishing to MQTT topic '%s' with QoS=1...", topic
            )

            # Publish as JSON string
            await mqtt.async_publish(
                self.hass, topic, json.dumps(payload), qos=1, retain=False
            )

            _LOGGER.info(
                "[MqttZ2mAdapter] Successfully published add_code for slot %d to '%s'",
                slot,
                topic,
            )

        except HomeAssistantError:
            raise
        except ImportError as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to import MQTT module: %s", err
            )
            raise HomeAssistantError(
                f"MQTT module not available: {err}"
            ) from err
        except Exception as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to publish add_code to MQTT: %s (type: %s)",
                err,
                type(err).__name__,
            )
            raise HomeAssistantError(f"Failed to add code via MQTT: {err}") from err

    async def remove_code(self, slot: int) -> None:
        """Remove a PIN code from the lock.

        Args:
            slot: User slot number to clear

        Raises:
            HomeAssistantError: If MQTT publish fails
        """
        topic = f"{self.base_topic}/set"
        
        # Nimly documentation: "set pincode to null to clear"
        # https://www.zigbee2mqtt.io/devices/Nimly.html
        payload = {
            "pin_code": {
                "user": slot,
                "user_enabled": False,
                "pin_code": None,  # null to clear the code
            }
        }

        _LOGGER.info(
            "[MqttZ2mAdapter] remove_code() called - slot=%d, topic='%s'",
            slot,
            topic,
        )
        _LOGGER.debug("[MqttZ2mAdapter] remove_code() payload: %s", json.dumps(payload))

        if not MQTT_ENABLED:
            _LOGGER.warning(
                "[MqttZ2mAdapter] DEV MODE - MQTT disabled. Would publish to '%s': %s",
                topic,
                json.dumps(payload),
            )
            return

        try:
            from homeassistant.components import mqtt

            # Check if MQTT is available
            if mqtt.DOMAIN not in self.hass.config.components:
                _LOGGER.error(
                    "[MqttZ2mAdapter] MQTT integration not loaded! Cannot publish."
                )
                raise HomeAssistantError(
                    "MQTT integration not loaded. Please configure MQTT in Home Assistant."
                )

            _LOGGER.debug(
                "[MqttZ2mAdapter] Publishing to MQTT topic '%s' with QoS=1...", topic
            )

            # Publish as JSON string
            await mqtt.async_publish(
                self.hass, topic, json.dumps(payload), qos=1, retain=False
            )

            _LOGGER.info(
                "[MqttZ2mAdapter] Successfully published remove_code for slot %d to '%s'",
                slot,
                topic,
            )

        except HomeAssistantError:
            raise
        except ImportError as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to import MQTT module: %s", err
            )
            raise HomeAssistantError(
                f"MQTT module not available: {err}"
            ) from err
        except Exception as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to publish remove_code to MQTT: %s (type: %s)",
                err,
                type(err).__name__,
            )
            raise HomeAssistantError(
                f"Failed to remove code via MQTT: {err}"
            ) from err

    async def verify_connection(self) -> bool:
        """Verify MQTT connection is available.

        Returns:
            True if MQTT is available, False otherwise
        """
        _LOGGER.debug("[MqttZ2mAdapter] verify_connection() called")

        if not MQTT_ENABLED:
            _LOGGER.warning(
                "[MqttZ2mAdapter] DEV MODE - MQTT disabled, returning True for connection check"
            )
            return True

        try:
            from homeassistant.components import mqtt

            is_loaded = mqtt.DOMAIN in self.hass.config.components
            _LOGGER.info(
                "[MqttZ2mAdapter] MQTT integration loaded: %s", is_loaded
            )

            if not is_loaded:
                _LOGGER.warning(
                    "[MqttZ2mAdapter] MQTT integration is NOT loaded. "
                    "Please ensure MQTT is configured in Home Assistant."
                )

            return is_loaded

        except ImportError as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to import MQTT module: %s", err
            )
            return False
        except Exception as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to verify MQTT connection: %s (type: %s)",
                err,
                type(err).__name__,
            )
            return False

    async def async_subscribe_credential_reports(
        self, storage: NimlykoderStorage
    ) -> Any:
        """Discover credentials reported in successful lock operations."""
        if not MQTT_ENABLED:
            return None

        try:
            from homeassistant.components import mqtt

            if mqtt.DOMAIN not in self.hass.config.components:
                return None

            async def handle_message(message: Any) -> None:
                try:
                    payload = json.loads(message.payload)
                except (TypeError, ValueError):
                    return
                if not isinstance(payload, dict):
                    return

                state = payload.get("state")
                if not isinstance(state, str):
                    return
                unlock_report = state.lower() == "unlock"
                prefix = "last_unlock" if unlock_report else "last_lock"
                report = (
                    state.lower(),
                    payload.get("last_unlock_source"),
                    payload.get("last_unlock_user"),
                    payload.get("last_lock_source"),
                    payload.get("last_lock_user"),
                )
                previous = getattr(self, "_last_credential_report", None)
                self._last_credential_report = report
                if getattr(message, "retain", False) or previous is None:
                    return

                identity = credential_from_operation(payload)
                if identity is None:
                    return
                source_key = f"{prefix}_source"
                user_key = f"{prefix}_user"
                if (
                    report == previous
                    or (
                        payload.get(source_key) == previous[1 if unlock_report else 3]
                        and payload.get(user_key) == previous[2 if unlock_report else 4]
                        and report[0] == previous[0]
                    )
                ):
                    return
                method, slot = identity
                await storage.discover(slot, method)

            return await mqtt.async_subscribe(
                self.hass, self.base_topic, handle_message, qos=1
            )
        except Exception as err:
            _LOGGER.warning(
                "Unable to subscribe to Zigbee2MQTT credential reports: %s",
                err,
            )
            return None
