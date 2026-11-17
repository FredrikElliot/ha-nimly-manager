"""Verify attribution sensor lifecycle with a small Home Assistant boundary."""
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1]


class SensorBase:
    async def async_added_to_hass(self):
        pass


class RestoreBase:
    pass


class ActivitySensorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        modules = {
            name: ModuleType(name)
            for name in (
                "homeassistant", "homeassistant.components",
                "homeassistant.components.sensor", "homeassistant.core",
                "homeassistant.helpers", "homeassistant.helpers.restore_state",
                "nimlykoder", "nimlykoder.activity", "nimlykoder.const",
            )
        }
        modules["homeassistant.components.sensor"].SensorEntity = SensorBase
        modules["homeassistant.core"].callback = lambda function: function
        modules["homeassistant.helpers.restore_state"].RestoreEntity = RestoreBase
        modules["nimlykoder.activity"].EVENT_LOCK_ACTIVITY = "nimlykoder_lock_activity"
        modules["nimlykoder.const"].DOMAIN = "nimlykoder"
        modules["nimlykoder.const"].CONF_LOCK_ENTITY = "lock_entity"
        self.modules_patch = patch.dict(sys.modules, modules)
        self.modules_patch.start()
        self.addCleanup(self.modules_patch.stop)
        spec = importlib.util.spec_from_file_location(
            "nimlykoder.sensor", ROOT / "custom_components/nimlykoder/sensor.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.data = {
            "config": {"lock_entity": "lock.front"},
            "activity": SimpleNamespace(last={}),
        }
        self.sensor = module.LockActivitySensor(
            self.data, SimpleNamespace(entry_id="front"), "unlock"
        )
        self.hass = SimpleNamespace(bus=SimpleNamespace(async_listen=Mock()))
        self.sensor.hass = self.hass
        self.sensor.async_get_last_state = AsyncMock(return_value=None)
        self.sensor.async_on_remove = Mock()
        self.sensor.async_write_ha_state = Mock()

    def emit(self, action="unlock", entry_id="front", name="Alex", method="pin"):
        self.data["activity"].last[action] = {
            "action": action, "name": name, "method": method,
            "source": "keypad", "slot": 1, "timestamp": "2026-11-17T00:00:01+00:00",
        }
        listener = self.hass.bus.async_listen.call_args.args[1]
        listener(SimpleNamespace(data={"entry_id": entry_id, "action": action}))

    async def test_only_matching_unlock_events_update_unlock_sensor(self):
        await self.sensor.async_added_to_hass()
        self.assertIsNone(self.sensor.native_value)
        self.emit()
        self.assertEqual(self.sensor.native_value, "Alex")
        self.emit(action="lock", name=None, method="automatic")
        self.assertEqual(self.sensor.native_value, "Alex")
        self.emit(entry_id="other", name="Someone else")
        self.assertEqual(self.sensor.native_value, "Alex")
        self.assertEqual(self.sensor.async_write_ha_state.call_count, 1)

    async def test_repeated_names_still_update_and_unattributed_clears_name(self):
        await self.sensor.async_added_to_hass()
        self.emit()
        self.emit()
        self.assertEqual(self.sensor.async_write_ha_state.call_count, 2)
        self.emit(name=None, method="remote")
        self.assertEqual(self.sensor.native_value, "remote")
        self.assertIsNone(self.sensor.extra_state_attributes["name"])
        self.emit(name=None, method="rfid")
        self.assertEqual(self.sensor.native_value, "unknown_credential")

    async def test_restore_does_not_emit_or_copy_unexpected_attributes(self):
        self.sensor.async_get_last_state.return_value = SimpleNamespace(attributes={
            "action": "unlock", "name": "Alex", "method": "pin",
            "last_used_pin_code": "secret",
        })
        await self.sensor.async_added_to_hass()
        self.assertEqual(self.sensor.native_value, "Alex")
        self.assertNotIn("last_used_pin_code", self.sensor.extra_state_attributes)
        self.sensor.async_write_ha_state.assert_not_called()
        self.assertEqual(self.sensor.async_on_remove.call_count, 1)


if __name__ == "__main__":
    unittest.main()
