"""Focused tests for Zigbee2MQTT protection and PIN-safe adapter logging."""
from __future__ import annotations

import asyncio
import json
import logging
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from homeassistant.components import mqtt
from homeassistant.exceptions import HomeAssistantError

from custom_components.nimlykoder.adapters import mqtt_z2m
from custom_components.nimlykoder.protection import resolve_z2m_device

TEST_PIN = "685209"
DEVICE_ID = "0x00124b0012345678"


class FilterMergeTests(unittest.TestCase):
    """Verify filter merging is additive and idempotent."""

    def test_merge_preserves_existing_filters_and_options(self) -> None:
        original = {
            "filtered_attributes": ["battery", "custom_.*"],
            "filtered_cache": ["linkquality"],
            "retain": True,
        }

        updated = mqtt_z2m.merge_sensitive_filters(original)

        self.assertEqual(
            updated["filtered_attributes"],
            ["battery", "custom_.*", "last_used_pin_code"],
        )
        self.assertEqual(
            updated["filtered_cache"], ["linkquality", "last_used_pin_code"]
        )
        self.assertTrue(updated["retain"])
        self.assertEqual(original["filtered_attributes"], ["battery", "custom_.*"])

    def test_merge_is_idempotent_and_preserves_inherited_filters(self) -> None:
        options = {
            "filtered_attributes": ["last_used_pin_code", "inherited"],
            "filtered_cache": ["last_used_pin_code"],
        }

        self.assertEqual(mqtt_z2m.merge_sensitive_filters(options), options)
        self.assertTrue(mqtt_z2m.has_sensitive_filters(options))


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    """Verify safe logging and the correlated bridge request flow."""

    def setUp(self) -> None:
        self.hass = SimpleNamespace(
            config=SimpleNamespace(components={"mqtt"})
        )
        self.adapter = mqtt_z2m.MqttZ2mAdapter(self.hass, "home/zigbee2mqtt")

    async def test_add_code_publishes_original_pin_without_logging_it(self) -> None:
        publish = AsyncMock()
        with (
            patch.object(mqtt_z2m, "MQTT_ENABLED", True),
            patch.object(mqtt, "async_publish", publish),
            self.assertLogs(mqtt_z2m._LOGGER, level=logging.DEBUG) as captured,
        ):
            await self.adapter.add_code(7, TEST_PIN)

        sent = json.loads(publish.await_args.args[2])
        self.assertEqual(sent["pin_code"]["pin_code"], int(TEST_PIN))
        self.assertNotIn(TEST_PIN, "\n".join(captured.output))

    async def test_disabled_and_failed_paths_do_not_log_pin(self) -> None:
        with (
            patch.object(mqtt_z2m, "MQTT_ENABLED", False),
            self.assertLogs(mqtt_z2m._LOGGER, level=logging.DEBUG) as captured,
        ):
            await self.adapter.add_code(7, TEST_PIN)
        self.assertNotIn(TEST_PIN, "\n".join(captured.output))

        publish = AsyncMock(side_effect=RuntimeError(f"failed payload {TEST_PIN}"))
        with (
            patch.object(mqtt_z2m, "MQTT_ENABLED", True),
            patch.object(mqtt, "async_publish", publish),
            self.assertLogs(mqtt_z2m._LOGGER, level=logging.DEBUG) as captured,
        ):
            with self.assertRaises(HomeAssistantError) as raised:
                await self.adapter.add_code(7, TEST_PIN)

        self.assertNotIn(TEST_PIN, "\n".join(captured.output))
        self.assertNotIn(TEST_PIN, str(raised.exception))

    async def test_request_subscribes_before_publish_and_correlates_response(self) -> None:
        events: list[str] = []
        callback = None

        async def subscribe(_hass, _topic, handler, qos):
            nonlocal callback
            events.append("subscribe")
            callback = handler
            return lambda: events.append("unsubscribe")

        async def publish(_hass, topic, payload, qos, retain):
            events.append("publish")
            request = json.loads(payload)
            self.assertEqual(topic, "home/zigbee2mqtt/bridge/request/device/options")
            callback(SimpleNamespace(
                payload=json.dumps(
                    {
                        "status": "ok",
                        "transaction": "unrelated",
                        "data": {"id": DEVICE_ID, "from": {}},
                    }
                )
            ))
            callback(SimpleNamespace(
                payload=json.dumps(
                    {
                        "status": "ok",
                        "transaction": request["transaction"],
                        "data": {"id": DEVICE_ID, "from": {"retain": True}},
                    }
                )
            ))

        with (
            patch.object(mqtt, "async_subscribe", subscribe),
            patch.object(mqtt, "async_publish", publish),
        ):
            result = await self.adapter._async_request_device_options(
                DEVICE_ID, {}
            )

        self.assertEqual(result["from"], {"retain": True})
        self.assertEqual(events, ["subscribe", "publish", "unsubscribe"])

    async def test_protection_merges_and_verifies_correct_device(self) -> None:
        original = {
            "filtered_attributes": ["battery"],
            "filtered_cache": ["linkquality"],
            "retain": True,
        }
        updated = mqtt_z2m.merge_sensitive_filters(original)
        request = AsyncMock(
            side_effect=[
                {"from": original},
                {"to": updated, "restart_required": True},
                {"from": updated},
            ]
        )
        with (
            patch.object(self.adapter, "_async_get_bridge_info", AsyncMock(return_value={"version": "2.0.0"})),
            patch.object(self.adapter, "_async_request_device_options", request),
        ):
            restart_required = await self.adapter.async_enable_sensitive_protection(
                DEVICE_ID
            )

        self.assertTrue(restart_required)
        self.assertEqual(request.call_args_list[1].args[0], DEVICE_ID)
        self.assertEqual(
            request.call_args_list[1].args[1],
            {
                "filtered_attributes": ["battery", "last_used_pin_code"],
                "filtered_cache": ["linkquality", "last_used_pin_code"],
            },
        )
        self.assertEqual(request.await_count, 3)

    async def test_existing_filters_are_verified_without_rewriting(self) -> None:
        options = {
            "filtered_attributes": ["last_used_pin_code"],
            "filtered_cache": ["last_used_pin_code"],
        }
        request = AsyncMock(return_value={"from": options})
        with (
            patch.object(self.adapter, "_async_get_bridge_info", AsyncMock(return_value={"version": "1.27.0"})),
            patch.object(self.adapter, "_async_request_device_options", request),
        ):
            restart_required = await self.adapter.async_enable_sensitive_protection(
                DEVICE_ID
            )

        self.assertFalse(restart_required)
        request.assert_awaited_once_with(DEVICE_ID, {})

    async def test_rejected_and_timed_out_requests_are_explicit(self) -> None:
        callback = None

        async def subscribe(_hass, _topic, handler, qos):
            nonlocal callback
            callback = handler
            return lambda: None

        async def rejected_publish(_hass, _topic, payload, qos, retain):
            request = json.loads(payload)
            callback(SimpleNamespace(
                payload=json.dumps(
                    {
                        "status": "error",
                        "transaction": request["transaction"],
                        "error": "Not authorized",
                    }
                )
            ))

        with (
            patch.object(mqtt, "async_subscribe", subscribe),
            patch.object(mqtt, "async_publish", rejected_publish),
        ):
            with self.assertRaises(mqtt_z2m.Zigbee2MqttProtectionError) as raised:
                await self.adapter._async_request_device_options(DEVICE_ID, {})
        self.assertEqual(raised.exception.code, "protection_permissions")

        async def timeout(waitable, timeout):
            if asyncio.iscoroutine(waitable):
                waitable.close()
            raise TimeoutError

        with (
            patch.object(mqtt, "async_subscribe", subscribe),
            patch.object(mqtt, "async_publish", AsyncMock()),
            patch.object(mqtt_z2m.asyncio, "wait_for", timeout),
        ):
            with self.assertRaises(mqtt_z2m.Zigbee2MqttProtectionError) as raised:
                await self.adapter._async_request_device_options(DEVICE_ID, {})
        self.assertEqual(raised.exception.code, "protection_timeout")


class DeviceResolutionTests(unittest.TestCase):
    """Verify the selected HA device resolves to a stable IEEE address."""

    def test_resolves_ieee_address_from_selected_mqtt_device(self) -> None:
        entity = SimpleNamespace(
            device_id="device-1", unique_id="lock_unique_id"
        )
        device = SimpleNamespace(
            identifiers={("mqtt", f"home/zigbee2mqtt_{DEVICE_ID}")}
        )
        with (
            patch(
                "custom_components.nimlykoder.protection.er.async_get",
                return_value=SimpleNamespace(
                    async_get=lambda _entity_id: entity
                ),
            ),
            patch(
                "custom_components.nimlykoder.protection.dr.async_get",
                return_value=SimpleNamespace(async_get=lambda _device_id: device),
            ),
        ):
            self.assertEqual(
                resolve_z2m_device(object(), "lock.front_door"),
                (DEVICE_ID, "home/zigbee2mqtt"),
            )


if __name__ == "__main__":
    unittest.main()
