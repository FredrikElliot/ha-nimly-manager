"""Focused activity tests; run with python -m unittest discover -s tests."""
import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "activity", ROOT / "custom_components/nimlykoder/activity.py"
)
activity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(activity)


class Names:
    def get_credential_name(self, method, slot):
        return {
            ("pin", 1): "PIN person",
            ("rfid", 1): "Tag person",
            ("fingerprint", 1): "Finger person",
            ("pin", 0): "Master",
        }.get((method, slot))


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.started = datetime(2026, 11, 17, tzinfo=timezone.utc)
        self.tracker = activity.LockActivity(Names(), self.started)

    def report(self, **overrides):
        return {
            "action": "unlock",
            "action_source_name": "keypad",
            "action_user": 1,
            "last_seen": (self.started + timedelta(seconds=1)).isoformat(),
            **overrides,
        }

    def test_names_are_scoped_by_method(self):
        for source, method, name in (
            ("keypad", "pin", "PIN person"),
            ("rfid", "rfid", "Tag person"),
            ("fingerprintsensor", "fingerprint", "Finger person"),
        ):
            with self.subTest(method=method):
                result = self.tracker.process(self.report(action_source_name=source))
                self.assertEqual(result["name"], name)
                self.assertEqual(result["method"], method)
                self.assertEqual(result["slot"], 1)

    def test_missing_unknown_and_invalid_slots_never_reuse_identity(self):
        self.tracker.process(self.report())
        for offset, slot in enumerate((None, 42, -1, 65535, True, 1.5, "invalid"), 2):
            result = self.tracker.process(self.report(
                action_user=slot,
                last_seen=(self.started + timedelta(seconds=offset)).isoformat(),
            ))
            self.assertIsNone(result["name"])
        self.assertEqual(self.tracker.process(self.report(
            action_user="1",
            last_seen=(self.started + timedelta(seconds=9)).isoformat(),
        ))["name"], "PIN person")

    def test_zero_slot_depends_on_source(self):
        self.assertEqual(self.tracker.process(self.report(action_user=0))["name"], "Master")
        for source, method in (
            ("self", "automatic"), ("zigbee", "remote"),
            ("manual", "manual"), ("unattributed", "unattributed"),
            ("unrecognized", "unknown"),
        ):
            result = self.tracker.process(
                self.report(action_user=0, action_source_name=source)
            )
            self.assertIsNone(result["name"])
            self.assertEqual(result["method"], method)

    def test_relocking_does_not_replace_last_unlock(self):
        unlocked = self.tracker.process(self.report())
        locked = self.tracker.process(
            self.report(action="lock", action_source_name="self", action_user=0)
        )
        self.assertEqual(self.tracker.last["unlock"], unlocked)
        self.assertEqual(self.tracker.last["lock"], locked)
        self.assertIsNone(locked["name"])

    def test_repeated_same_person_is_not_debounced(self):
        first = self.tracker.process(self.report())
        second = self.tracker.process(self.report(
            last_seen=(self.started + timedelta(seconds=2)).isoformat()
        ))
        self.assertEqual(first["name"], second["name"])
        self.assertNotEqual(first["timestamp"], second["timestamp"])
        self.assertIsNone(self.tracker.process(self.report()))

    def test_identical_report_is_deduplicated(self):
        self.assertIsNotNone(self.tracker.process(self.report()))
        self.assertIsNone(self.tracker.process(self.report()))

    def test_startup_completion_advances_freshness_boundary(self):
        self.tracker.started = self.started + timedelta(seconds=2)
        self.assertIsNone(self.tracker.process(self.report()))
        self.assertIsNotNone(self.tracker.process(self.report(
            last_seen=(self.started + timedelta(seconds=3)).isoformat()
        )))

    def test_retained_startup_and_unrelated_state_are_ignored(self):
        for payload in (
            self.report(last_seen=self.started.isoformat()),
            self.report(last_seen=(self.started - timedelta(days=1)).isoformat()),
            self.report(last_seen=None),
            self.report(last_seen="invalid"),
            self.report(last_seen=True),
            {"state": "UNLOCK", "last_unlock_user": "1", "last_unlock_source": "keypad"},
            self.report(action="pin_code_added"),
            self.report(action=None),
            [],
        ):
            with self.subTest(payload=payload):
                self.assertIsNone(self.tracker.process(payload))
        self.assertIsNone(self.tracker.process(self.report(), retained=True))
        report = self.report()
        del report["action_source_name"]
        self.assertIsNone(self.tracker.process(report))
        self.assertEqual(self.tracker.last, {})

    def test_epoch_and_epoch_ms(self):
        timestamp = (self.started + timedelta(seconds=1)).timestamp()
        for value in (timestamp, timestamp * 1000):
            tracker = activity.LockActivity(Names(), self.started)
            self.assertEqual(
                tracker.process(self.report(last_seen=value))["timestamp"],
                self.report()["last_seen"],
            )

    def test_payload_secrets_are_not_copied(self):
        result = self.tracker.process(self.report(
            last_used_pin_code="123456", pin_code="123456",
            rfid="secret", fingerprint="biometric",
        ))
        self.assertEqual(
            set(result), {"action", "name", "method", "source", "slot", "timestamp"}
        )
        self.assertNotIn("123456", str(result))
        self.assertNotIn("biometric", str(result))


if __name__ == "__main__":
    unittest.main()
