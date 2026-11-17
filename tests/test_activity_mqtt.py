"""Exercise the MQTT boundary without a running Home Assistant installation."""
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1]


class MqttActivityTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        modules = {
            name: ModuleType(name)
            for name in (
                "homeassistant", "homeassistant.core", "homeassistant.components",
                "homeassistant.components.mqtt", "homeassistant.exceptions",
            )
        }
        modules["homeassistant.core"].HomeAssistant = object
        modules["homeassistant.core"].callback = lambda function: function
        modules["homeassistant.exceptions"].HomeAssistantError = RuntimeError
        self.mqtt = modules["homeassistant.components.mqtt"]
        self.unsubscribe = Mock()
        self.mqtt.async_subscribe = AsyncMock(return_value=self.unsubscribe)
        self.modules_patch = patch.dict(sys.modules, modules)
        self.modules_patch.start()
        self.addCleanup(self.modules_patch.stop)
        spec = importlib.util.spec_from_file_location(
            "mqtt_z2m", ROOT / "custom_components/nimlykoder/adapters/mqtt_z2m.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.hass = SimpleNamespace(is_running=True)
        self.adapter = module.MqttZ2mAdapter(self.hass, "zigbee2mqtt/front/")
        self.handler = Mock()
        self.assertIs(
            await self.adapter.async_subscribe_activity(self.handler), self.unsubscribe
        )
        self.received = self.mqtt.async_subscribe.call_args.args[2]

    def send(self, payload, retained=False):
        self.received(SimpleNamespace(payload=payload, retain=retained))

    async def test_existing_topic_and_connection_are_used(self):
        self.assertEqual(self.mqtt.async_subscribe.call_args.args[:2],
                         (self.hass, "zigbee2mqtt/front"))
        self.assertEqual(self.mqtt.async_subscribe.call_args.kwargs, {"qos": 0})

    async def test_startup_retained_and_malformed_messages_are_ignored(self):
        self.send(json.dumps({"action": "unlock"}), retained=True)
        self.hass.is_running = False
        self.send(json.dumps({"action": "unlock"}))
        self.hass.is_running = True
        self.send("invalid JSON")
        self.send(b"\xff")
        self.handler.assert_not_called()

    async def test_each_live_message_reaches_activity_parser(self):
        report = {"action": "unlock", "action_user": 1, "action_source_name": "keypad"}
        self.send(json.dumps(report))
        self.send(json.dumps(report))
        self.assertEqual(self.handler.call_count, 2)
        self.handler.assert_called_with(report)


if __name__ == "__main__":
    unittest.main()
