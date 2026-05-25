"""Tests for the Control Panel status model (pure parts; no Cinema 4D).

The :class:`UIStatus` model and its concise label helpers must work in plain
Python, and ``collect_status(None)`` must return a safe all-unknown snapshot
without importing ``c4d``. The module must not import ``c4d`` at top level.
"""

import unittest

from openrelativity_c4d.c4d import ui_status
from openrelativity_c4d.c4d.ui_status import UIStatus


class TestModuleIsImportSafe(unittest.TestCase):
    def test_no_c4d_dependency(self):
        self.assertFalse(hasattr(ui_status, "c4d"))


class TestLabels(unittest.TestCase):
    def test_ok_missing_unknown(self):
        self.assertEqual(UIStatus(controller=True).controller_label(), "OK")
        self.assertEqual(UIStatus(controller=False).controller_label(), "Missing")
        self.assertEqual(UIStatus(controller=None).controller_label(), "Unknown")
        self.assertEqual(UIStatus(camera=True).camera_label(), "OK")
        self.assertEqual(UIStatus(camera=False).camera_label(), "Missing")

    def test_objects_label(self):
        self.assertEqual(UIStatus(object_count=3).objects_label(), "3")
        self.assertEqual(UIStatus(object_count=0).objects_label(), "0")
        self.assertEqual(UIStatus(object_count=None).objects_label(), "?")

    def test_generated_label(self):
        self.assertEqual(
            UIStatus(preview_materials=2, lorentz_copies=1).generated_label(),
            "2 mat / 1 Lorentz")
        self.assertEqual(UIStatus().generated_label(), "? mat / ? Lorentz")

    def test_octane_tristate(self):
        self.assertEqual(UIStatus(octane=ui_status.OCTANE_DETECTED).octane_label(),
                         "Detected")
        self.assertEqual(UIStatus(octane=ui_status.OCTANE_MISSING).octane_label(),
                         "Missing")
        self.assertEqual(UIStatus(octane=ui_status.OCTANE_UNKNOWN).octane_label(),
                         "Unknown")
        self.assertEqual(UIStatus(octane="something else").octane_label(), "Unknown")

    def test_last_label_defaults(self):
        self.assertEqual(UIStatus().last_label(), "(none yet)")
        self.assertEqual(UIStatus(last_action="Ran: Apply Doppler").last_label(),
                         "Ran: Apply Doppler")

    def test_format_summary_is_a_string(self):
        text = UIStatus(controller=True, object_count=2).format_summary()
        self.assertIsInstance(text, str)
        self.assertIn("Controller: OK", text)
        self.assertIn("Objects:    2", text)


class TestCollectStatusNoDoc(unittest.TestCase):
    def test_none_doc_is_all_unknown_and_safe(self):
        status = ui_status.collect_status(None, last_action="hi")
        self.assertIsInstance(status, UIStatus)
        self.assertEqual(status.controller_label(), "Unknown")
        self.assertEqual(status.camera_label(), "Unknown")
        self.assertEqual(status.objects_label(), "?")
        self.assertEqual(status.octane_label(), "Unknown")
        self.assertEqual(status.last_label(), "hi")


if __name__ == "__main__":
    unittest.main()
