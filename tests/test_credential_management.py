"""Focused tests for credential identity, discovery, and localization."""
from __future__ import annotations

import importlib
import json
import sys
import types
import unittest
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "nimlykoder"
sys.path.insert(0, str(ROOT))


class _FakeStore:
    def __init__(self, _hass, _version, _key):
        self.data = None

    async def async_load(self):
        return self.data

    async def async_save(self, data):
        self.data = data


def _install_home_assistant_test_stubs():
    homeassistant = types.ModuleType("homeassistant")
    homeassistant.__path__ = []
    core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    exceptions = types.ModuleType("homeassistant.exceptions")

    class HomeAssistantError(Exception):
        pass

    exceptions.HomeAssistantError = HomeAssistantError
    helpers = types.ModuleType("homeassistant.helpers")
    helpers.__path__ = []
    storage_module = types.ModuleType("homeassistant.helpers.storage")
    storage_module.Store = _FakeStore
    sys.modules.update(
        {
            "homeassistant": homeassistant,
            "homeassistant.core": core,
            "homeassistant.exceptions": exceptions,
            "homeassistant.helpers": helpers,
            "homeassistant.helpers.storage": storage_module,
        }
    )

    component_package = types.ModuleType("custom_components.nimlykoder")
    component_package.__path__ = [str(COMPONENT)]
    component_package.__package__ = "custom_components.nimlykoder"
    sys.modules["custom_components.nimlykoder"] = component_package


_install_home_assistant_test_stubs()
const = importlib.import_module("custom_components.nimlykoder.const")
events = importlib.import_module("custom_components.nimlykoder.credential_events")
policy = importlib.import_module("custom_components.nimlykoder.credential_policy")
storage_module = importlib.import_module("custom_components.nimlykoder.storage")
adapter_module = importlib.import_module(
    "custom_components.nimlykoder.adapters.mqtt_z2m"
)


class CredentialEventTests(unittest.TestCase):
    def test_maps_successful_credential_sources_to_method_and_slot(self):
        self.assertEqual(
            events.credential_from_operation(
                {
                    "state": "UNLOCK",
                    "last_unlock_source": "keypad",
                    "last_unlock_user": "1",
                    "last_used_pin_code": 123456,
                }
            ),
            (const.CREDENTIAL_PIN, 1),
        )
        self.assertEqual(
            events.credential_from_operation(
                {
                    "state": "UNLOCK",
                    "last_unlock_source": "rfid",
                    "last_unlock_user": 1,
                }
            ),
            (const.CREDENTIAL_TAG, 1),
        )
        self.assertEqual(
            events.credential_from_operation(
                {
                    "state": "LOCK",
                    "last_lock_source": "fingerprintsensor",
                    "last_lock_user": 1,
                }
            ),
            (const.CREDENTIAL_FINGERPRINT, 1),
        )

    def test_rejects_remote_failed_and_unattributed_reports(self):
        for payload in (
            {"state": "UNLOCK", "last_unlock_source": "zigbee", "last_unlock_user": 1},
            {"state": "UNLOCK", "last_unlock_source": "unattributed", "last_unlock_user": 1},
            {"state": "UNLOCK", "last_unlock_source": "unknown", "last_unlock_user": 1},
            {"state": "LOCKED", "last_unlock_source": "keypad", "last_unlock_user": 1},
            {"state": "UNLOCK", "last_unlock_source": "keypad"},
            {"state": "UNLOCK", "last_unlock_source": "keypad", "last_unlock_user": 1000},
            {"state": "UNLOCK", "last_unlock_source": "keypad", "last_unlock_user": True},
            {"last_unlock_source": "keypad", "last_unlock_user": 1},
        ):
            with self.subTest(payload=payload):
                self.assertIsNone(events.credential_from_operation(payload))

    def test_reserved_pin_slots_include_master_and_configured_slots(self):
        self.assertTrue(policy.is_reserved_pin_slot(0, [1, 2, 3]))
        self.assertTrue(policy.is_reserved_pin_slot(2, [1, 2, 3]))
        self.assertFalse(policy.is_reserved_pin_slot(4, [1, 2, 3]))


class MqttDiscoveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_retained_and_remote_reports_do_not_create_credentials_or_store_pin(self):
        subscriptions = []
        mqtt = types.ModuleType("homeassistant.components.mqtt")
        mqtt.DOMAIN = "mqtt"

        async def async_subscribe(_hass, _topic, callback, qos):
            subscriptions.append((callback, qos))
            return lambda: None

        mqtt.async_subscribe = async_subscribe
        components = types.ModuleType("homeassistant.components")
        components.__path__ = []
        components.mqtt = mqtt
        sys.modules["homeassistant.components"] = components
        sys.modules["homeassistant.components.mqtt"] = mqtt

        class FakeHass:
            class config:
                components = {"mqtt"}

        class Message:
            def __init__(self, payload, retain=False):
                self.payload = json.dumps(payload)
                self.retain = retain

        storage = storage_module.NimlykoderStorage(None)
        adapter = adapter_module.MqttZ2mAdapter(FakeHass(), "zigbee2mqtt/front_door")
        await adapter.async_subscribe_credential_reports(storage)
        callback, qos = subscriptions[0]
        self.assertEqual(qos, 1)

        await callback(
            Message(
                {
                    "state": "LOCK",
                    "last_unlock_source": "keypad",
                    "last_unlock_user": 6,
                },
                retain=True,
            )
        )
        self.assertEqual(storage.list_entries(), [])
        await callback(
            Message(
                {
                    "state": "UNLOCK",
                    "last_unlock_source": "keypad",
                    "last_unlock_user": 6,
                    "last_used_pin_code": 483729,
                }
            )
        )
        self.assertIsNotNone(storage.get(6, const.CREDENTIAL_PIN))
        self.assertNotIn("483729", json.dumps(storage._store.data))

        await callback(
            Message(
                {
                    "state": "LOCK",
                    "last_lock_source": "zigbee",
                    "last_lock_user": 0,
                    "last_unlock_source": "keypad",
                    "last_unlock_user": 6,
                }
            )
        )
        await callback(
            Message(
                {
                    "state": "UNLOCK",
                    "last_unlock_source": "zigbee",
                    "last_unlock_user": 9,
                }
            )
        )
        self.assertIsNone(storage.get(9, const.CREDENTIAL_PIN))


class CredentialStorageTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.storage = storage_module.NimlykoderStorage(None)

    async def test_migrates_existing_entries_as_pins_without_metadata_loss(self):
        self.storage._store.data = {
            "version": 1,
            "entries": {
                "8": {
                    "name": "Guest",
                    "type": "guest",
                    "expiry": "2030-01-02",
                    "created": "2026-01-01T10:00:00",
                    "updated": "2026-01-02T10:00:00",
                }
            },
        }

        await self.storage.async_load()

        migrated = self.storage.get(8)
        self.assertEqual(migrated.method, const.CREDENTIAL_PIN)
        self.assertEqual(migrated.name, "Guest")
        self.assertEqual(migrated.expiry, "2030-01-02")
        self.assertEqual(migrated.created, "2026-01-01T10:00:00")
        self.assertEqual(migrated.updated, "2026-01-02T10:00:00")
        self.assertFalse(migrated.discovered)
        self.assertEqual(self.storage._store.data["version"], const.STORAGE_VERSION)

    async def test_discovery_is_idempotent_and_method_scoped(self):
        managed = await self.storage.add(
            1, "Managed PIN", const.TYPE_GUEST, "2030-01-02"
        )
        pin_created = managed.created
        await self.storage.discover(1, const.CREDENTIAL_PIN)
        tag = await self.storage.discover(1, const.CREDENTIAL_TAG)
        fingerprint = await self.storage.discover(1, const.CREDENTIAL_FINGERPRINT)
        await self.storage.update_name(1, "Front door tag", const.CREDENTIAL_TAG)
        await self.storage.discover(1, const.CREDENTIAL_TAG)

        self.assertEqual(self.storage.get(1).name, "Managed PIN")
        self.assertEqual(self.storage.get(1).expiry, "2030-01-02")
        self.assertEqual(self.storage.get(1).created, pin_created)
        self.assertEqual(self.storage.get(1, const.CREDENTIAL_TAG).name, "Front door tag")
        self.assertIsNone(self.storage.get(1, const.CREDENTIAL_FINGERPRINT).name)
        self.assertTrue(tag.discovered)
        self.assertTrue(fingerprint.discovered)
        self.assertEqual(
            {(entry.method, entry.slot) for entry in self.storage.list_entries()},
            {
                (const.CREDENTIAL_PIN, 1),
                (const.CREDENTIAL_TAG, 1),
                (const.CREDENTIAL_FINGERPRINT, 1),
            },
        )
        self.assertNotIn("pin_code", tag.to_dict())

    async def test_removal_and_expiry_cleanup_are_method_safe(self):
        await self.storage.discover(4, const.CREDENTIAL_PIN)
        await self.storage.discover(4, const.CREDENTIAL_TAG)
        await self.storage.discover(4, const.CREDENTIAL_FINGERPRINT)
        await self.storage.remove(4, const.CREDENTIAL_TAG)

        self.assertIsNone(self.storage.get(4, const.CREDENTIAL_TAG))
        self.assertIsNotNone(self.storage.get(4, const.CREDENTIAL_PIN))
        self.assertIsNotNone(self.storage.get(4, const.CREDENTIAL_FINGERPRINT))

        await self.storage.add(5, "Expired PIN", const.TYPE_GUEST, "2000-01-01")
        await self.storage.discover(4, const.CREDENTIAL_TAG)
        tag_data = self.storage._data["tag:4"]
        tag_data["type"] = const.TYPE_GUEST
        tag_data["expiry"] = "2000-01-01"
        self.assertEqual(self.storage.expired_guest_slots(date.today()), [5])
        with self.assertRaises(Exception):
            await self.storage.update_expiry(4, "2030-01-01", const.CREDENTIAL_TAG)


class TranslationTests(unittest.TestCase):
    def test_manual_name_is_localized_and_not_a_stored_value(self):
        english = json.loads(
            (COMPONENT / "panel_translations" / "en.json").read_text()
        )
        swedish = json.loads(
            (COMPONENT / "panel_translations" / "sv.json").read_text()
        )
        self.assertEqual(english["manually_configured"], "Manually configured")
        self.assertEqual(swedish["manually_configured"], "Manuellt konfigurerad")


if __name__ == "__main__":
    unittest.main()
