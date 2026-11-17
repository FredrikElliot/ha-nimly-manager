"""Exercise credential-name storage without installing Home Assistant."""
import copy
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1]


class CredentialNameTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        package_name = "_credential_names_test"
        modules = {
            name: ModuleType(name)
            for name in (
                "homeassistant", "homeassistant.core", "homeassistant.helpers",
                "homeassistant.helpers.storage", "homeassistant.exceptions",
                package_name,
            )
        }
        modules[package_name].__path__ = [
            str(ROOT / "custom_components/nimlykoder")
        ]
        modules["homeassistant.core"].HomeAssistant = object
        modules["homeassistant.exceptions"].HomeAssistantError = RuntimeError
        self.saved_data = None

        async def save(data):
            self.saved_data = copy.deepcopy(data)

        self.store = SimpleNamespace(
            async_load=AsyncMock(return_value=None),
            async_save=AsyncMock(side_effect=save),
        )
        modules["homeassistant.helpers.storage"].Store = Mock(
            return_value=self.store
        )
        for name in ("const", "storage"):
            spec = importlib.util.spec_from_file_location(
                f"{package_name}.{name}",
                ROOT / "custom_components/nimlykoder" / f"{name}.py",
            )
            modules[spec.name] = importlib.util.module_from_spec(spec)
        modules_patch = patch.dict(sys.modules, modules)
        modules_patch.start()
        self.addCleanup(modules_patch.stop)
        for name in ("const", "storage"):
            module = modules[f"{package_name}.{name}"]
            module.__spec__.loader.exec_module(module)
        self.storage_class = modules[f"{package_name}.storage"].NimlykoderStorage
        self.storage = self.storage_class(object())
        await self.storage.async_load()

    async def add_pin(self, slot=7):
        return await self.storage.add(slot, "PIN owner", "permanent")

    async def reload_storage(self):
        self.store.async_load.return_value = copy.deepcopy(self.saved_data)
        storage = self.storage_class(object())
        await storage.async_load()
        return storage

    async def test_pin_names_follow_existing_pin_apis(self):
        await self.add_pin()
        self.assertEqual(self.storage.get_credential_name("pin", 7), "PIN owner")
        await self.storage.update_name(7, "Updated PIN owner")
        self.assertEqual(
            self.storage.get_credential_name("pin", 7), "Updated PIN owner"
        )
        await self.storage.remove(7)
        self.assertIsNone(self.storage.get_credential_name("pin", 7))

    async def test_same_slot_names_are_isolated_by_method(self):
        pin = await self.add_pin()
        await self.storage.set_credential_name("rfid", 7, "Card owner")
        await self.storage.set_credential_name("fingerprint", 7, "Finger owner")
        for method, expected in (
            ("pin", "PIN owner"),
            ("rfid", "Card owner"),
            ("fingerprint", "Finger owner"),
        ):
            self.assertEqual(self.storage.get_credential_name(method, 7), expected)
        self.assertEqual(self.storage.get(7), pin)
        self.assertEqual(self.storage.list_entries(), [pin])
        self.assertFalse(self.storage.is_slot_occupied(8))
        await self.storage.set_credential_name("rfid", 8, "Another card")
        self.assertFalse(self.storage.is_slot_occupied(8))

    async def test_old_storage_without_mapping_loads_unchanged(self):
        pin = await self.add_pin()
        old_data = copy.deepcopy(self.saved_data)
        old_data.pop("credential_names")
        for include_version in (True, False):
            with self.subTest(include_version=include_version):
                data = copy.deepcopy(old_data)
                if not include_version:
                    data.pop("version")
                self.store.async_load.return_value = data
                await self.storage.async_load()
                self.assertEqual(self.storage.get(7), pin)
                self.assertEqual(
                    self.storage.get_credential_name("pin", 7), "PIN owner"
                )
                self.assertIsNone(self.storage.get_credential_name("rfid", 7))
                self.assertIsNone(
                    self.storage.get_credential_name("fingerprint", 7)
                )

    async def test_names_are_saved_and_reloaded_without_changing_pins(self):
        pin = await self.add_pin()
        await self.storage.set_credential_name("rfid", 0, " First card ")
        await self.storage.set_credential_name("fingerprint", 65534, "Last finger")
        self.store.async_save.assert_awaited()
        self.assertEqual(
            self.saved_data["credential_names"],
            {"rfid": {"0": "First card"}, "fingerprint": {"65534": "Last finger"}},
        )
        reloaded = await self.reload_storage()
        self.assertEqual(reloaded.get_credential_name("rfid", 0), "First card")
        self.assertEqual(
            reloaded.get_credential_name("fingerprint", 65534), "Last finger"
        )
        self.assertEqual(reloaded.get(7), pin)

    async def test_empty_names_delete_only_selected_mapping_and_persist(self):
        await self.add_pin()
        await self.storage.set_credential_name("rfid", 7, "Card owner")
        await self.storage.set_credential_name("fingerprint", 7, "Finger owner")
        await self.storage.set_credential_name("rfid", 7, "")
        reloaded = await self.reload_storage()
        self.assertIsNone(reloaded.get_credential_name("rfid", 7))
        self.assertEqual(
            reloaded.get_credential_name("fingerprint", 7), "Finger owner"
        )
        self.assertEqual(reloaded.get_credential_name("pin", 7), "PIN owner")
        await self.storage.set_credential_name("fingerprint", 7, "   ")
        reloaded = await self.reload_storage()
        self.assertIsNone(reloaded.get_credential_name("fingerprint", 7))
        await self.storage.set_credential_name("rfid", 999, "")
        self.assertIsNone(self.storage.get_credential_name("rfid", 999))

    async def test_invalid_setter_inputs_do_not_save(self):
        self.store.async_save.reset_mock()
        for method, slot, name in (
            ("pin", 7, "Not a PIN rename"),
            ("unknown", 7, "Unknown method"),
            (None, 7, "Missing method"),
            ("rfid", -1, "Negative slot"),
            ("fingerprint", 65536, "Oversized slot"),
            ("rfid", True, "Boolean slot"),
            ("rfid", 1.5, "Float slot"),
            ("rfid", "7", "String slot"),
            ("rfid", None, "Missing slot"),
            ("rfid", 7, None),
            ("fingerprint", 7, 123),
        ):
            with self.subTest(method=method, slot=slot, name=name):
                with self.assertRaises(ValueError):
                    await self.storage.set_credential_name(method, slot, name)
        self.store.async_save.assert_not_awaited()

    async def test_unknown_names_and_invalid_lookups_return_none(self):
        await self.add_pin()
        for method, slot in (
            ("pin", 8), ("rfid", 7), ("fingerprint", 7), ("unknown", 7),
            (None, 7), ("pin", -1), ("rfid", 65536), ("pin", True),
            ("pin", 7.0), ("pin", "7"), ("fingerprint", None),
        ):
            with self.subTest(method=method, slot=slot):
                self.assertIsNone(self.storage.get_credential_name(method, slot))

    async def test_failed_save_rolls_back_add_update_and_delete(self):
        await self.add_pin()
        await self.storage.set_credential_name("rfid", 7, "Card owner")
        await self.storage.set_credential_name("fingerprint", 7, "Finger owner")
        persisted = copy.deepcopy(self.saved_data)
        self.store.async_save.side_effect = OSError("Storage unavailable")
        for method, slot, name in (
            ("rfid", 8, "New card"),
            ("rfid", 7, "Changed card"),
            ("rfid", 7, ""),
        ):
            with self.subTest(method=method, slot=slot, name=name):
                with self.assertRaises(OSError):
                    await self.storage.set_credential_name(method, slot, name)
                self.assertIsNone(self.storage.get_credential_name("rfid", 8))
                self.assertEqual(
                    self.storage.get_credential_name("rfid", 7), "Card owner"
                )
                self.assertEqual(
                    self.storage.get_credential_name("fingerprint", 7),
                    "Finger owner",
                )
                self.assertEqual(
                    self.storage.get_credential_name("pin", 7), "PIN owner"
                )
                self.assertEqual(self.saved_data, persisted)


if __name__ == "__main__":
    unittest.main()
