"""MQTT adapter for Zigbee2MQTT communication with Nimly locks."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

# Set to True to enable actual MQTT communication
# Set to False for development/testing without MQTT
MQTT_ENABLED = True


class Zigbee2MqttProtectionError(HomeAssistantError):
    """A safe, user-facing error while configuring Zigbee2MQTT protection."""

    def __init__(self, code: str) -> None:
        """Initialize with a translated error code."""
        self.code = code
        super().__init__(code)


def merge_sensitive_filters(options: dict[str, Any]) -> dict[str, Any]:
    """Return device options with both last-used PIN filters, preserving all else."""
    merged = dict(options)
    for key in ("filtered_attributes", "filtered_cache"):
        existing = merged.get(key, [])
        if not isinstance(existing, list):
            raise Zigbee2MqttProtectionError("protection_unsupported")
        merged[key] = list(dict.fromkeys([*existing, "last_used_pin_code"]))
    return merged


def has_sensitive_filters(options: dict[str, Any]) -> bool:
    """Return whether both supported filters contain the PIN attribute."""
    return all(
        isinstance(options.get(key), list)
        and "last_used_pin_code" in options[key]
        for key in ("filtered_attributes", "filtered_cache")
    )


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
            "[MqttZ2mAdapter] add_code() called - slot=%d, PIN length=%d, user_type=%s, topic='%s'",
            slot,
            len(pin_code),
            user_type,
            topic,
        )
        _LOGGER.debug(
            "[MqttZ2mAdapter] add_code() prepared command for slot %d", slot
        )

        if not MQTT_ENABLED:
            _LOGGER.warning(
                "[MqttZ2mAdapter] DEV MODE - MQTT disabled. Would publish add_code for slot %d to '%s' (payload omitted)",
                slot,
                topic,
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

        except HomeAssistantError as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to publish add_code (type: %s)",
                type(err).__name__,
            )
            raise HomeAssistantError("Failed to add code via MQTT.") from None
        except ImportError as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to import MQTT module (type: %s)",
                type(err).__name__,
            )
            raise HomeAssistantError("MQTT module not available.") from None
        except Exception as err:
            _LOGGER.error(
                "[MqttZ2mAdapter] Failed to publish add_code to MQTT (type: %s)",
                type(err).__name__,
            )
            raise HomeAssistantError("Failed to add code via MQTT.") from None

    async def async_enable_sensitive_protection(
        self, device_id: str
    ) -> bool:
        """Protect Nimly's last-used PIN from device publications and cache.

        Returns whether Zigbee2MQTT reports that a restart is required.
        """
        info = await self._async_get_bridge_info()
        version = info.get("version")
        if isinstance(version, dict):
            version = version.get("version")
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)", str(version or ""))
        if not match or tuple(map(int, match.groups())) < (1, 27, 0):
            raise Zigbee2MqttProtectionError("protection_unsupported")

        current = await self._async_request_device_options(device_id, {})
        current_options = current.get("from", {})
        if not isinstance(current_options, dict):
            raise Zigbee2MqttProtectionError("protection_unsupported")

        merged = merge_sensitive_filters(current_options)

        if has_sensitive_filters(current_options):
            return False

        updated = await self._async_request_device_options(
            device_id,
            {
                "filtered_attributes": merged["filtered_attributes"],
                "filtered_cache": merged["filtered_cache"],
            },
        )
        resulting_options = updated.get("to", {})
        if not isinstance(resulting_options, dict) or not has_sensitive_filters(
            resulting_options
        ):
            raise Zigbee2MqttProtectionError("protection_unsupported")

        verified = await self._async_request_device_options(device_id, {})
        verified_options = verified.get("from", {})
        if not isinstance(verified_options, dict) or not has_sensitive_filters(
            verified_options
        ):
            raise Zigbee2MqttProtectionError("protection_rejected")

        return bool(updated.get("restart_required"))

    async def _async_get_bridge_info(self) -> dict[str, Any]:
        """Read retained bridge information, including its Zigbee2MQTT version."""
        from homeassistant.components import mqtt

        if mqtt.DOMAIN not in self.hass.config.components:
            raise Zigbee2MqttProtectionError("protection_mqtt_unavailable")

        future: asyncio.Future[dict[str, Any]] = (
            asyncio.get_running_loop().create_future()
        )
        topic = f"{self.base_topic}/bridge/info"

        def handle_message(message: Any) -> None:
            if future.done():
                return
            try:
                data = json.loads(message.payload)
            except (TypeError, ValueError):
                return
            if isinstance(data, dict):
                future.set_result(data)

        try:
            unsubscribe = await mqtt.async_subscribe(
                self.hass, topic, handle_message, qos=1
            )
        except Exception as err:
            raise Zigbee2MqttProtectionError(
                self._protection_error_code(err)
            ) from None
        try:
            return await asyncio.wait_for(future, timeout=5)
        except TimeoutError:
            raise Zigbee2MqttProtectionError("protection_timeout") from None
        finally:
            unsubscribe()

    async def _async_request_device_options(
        self, device_id: str, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Send a correlated device-options request and validate its response."""
        from homeassistant.components import mqtt

        if mqtt.DOMAIN not in self.hass.config.components:
            raise Zigbee2MqttProtectionError("protection_mqtt_unavailable")

        transaction = uuid.uuid4().hex
        response_topic = f"{self.base_topic}/bridge/response/device/options"
        request_topic = f"{self.base_topic}/bridge/request/device/options"
        future: asyncio.Future[dict[str, Any]] = (
            asyncio.get_running_loop().create_future()
        )

        def handle_message(message: Any) -> None:
            if future.done():
                return
            try:
                response = json.loads(message.payload)
            except (TypeError, ValueError):
                return
            if (
                isinstance(response, dict)
                and response.get("transaction") == transaction
            ):
                future.set_result(response)

        try:
            unsubscribe = await mqtt.async_subscribe(
                self.hass, response_topic, handle_message, qos=1
            )
        except Exception as err:
            raise Zigbee2MqttProtectionError(
                self._protection_error_code(err)
            ) from None
        try:
            await mqtt.async_publish(
                self.hass,
                request_topic,
                json.dumps(
                    {"id": device_id, "options": options, "transaction": transaction}
                ),
                qos=1,
                retain=False,
            )
            response = await asyncio.wait_for(future, timeout=10)
        except TimeoutError:
            raise Zigbee2MqttProtectionError("protection_timeout") from None
        except Exception as err:
            raise Zigbee2MqttProtectionError(
                self._protection_error_code(err)
            ) from None
        finally:
            unsubscribe()

        if response.get("status") != "ok":
            error = str(response.get("error", response.get("message", ""))).lower()
            code = (
                "protection_permissions"
                if any(word in error for word in ("not authorized", "permission", "access denied"))
                else "protection_rejected"
            )
            raise Zigbee2MqttProtectionError(code)

        data = response.get("data")
        if not isinstance(data, dict) or data.get("id") != device_id:
            raise Zigbee2MqttProtectionError("protection_rejected")
        return data

    @staticmethod
    def _protection_error_code(err: Exception) -> str:
        """Classify a bridge error without including its text in logs or UI."""
        text = str(err).lower()
        if any(
            word in text
            for word in ("not authorized", "permission", "access denied")
        ):
            return "protection_permissions"
        return "protection_rejected"

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
