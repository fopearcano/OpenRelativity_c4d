"""Tests for the Octane detection layer.

These verify the core guarantee: importing and using the Octane detection layer
is safe when neither Octane nor Cinema 4D is present (this very test runs in
plain Python). They must not import ``c4d``.
"""

import unittest

from openrelativity_c4d.octane import detection


class TestOctaneDetectionIsSafe(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        # The detection module must not import c4d at module scope.
        self.assertFalse(hasattr(detection, "c4d"))

    def test_detect_returns_false_without_octane(self):
        # No Octane / no Cinema 4D here -> must be False, never raise.
        self.assertIs(detection.detect_octane_available(), False)

    def test_backwards_compatible_alias(self):
        self.assertIs(detection.is_octane_available, detection.detect_octane_available)

    def test_octane_module_is_none(self):
        self.assertIsNone(detection.octane_module())

    def test_named_plugins_empty_without_c4d(self):
        self.assertEqual(detection._named_octane_plugins(), [])


class TestOctaneStatusReport(unittest.TestCase):
    def test_report_has_expected_keys(self):
        report = detection.get_octane_status_report(None)
        for key in ("octane_detected", "octane_renderer_active",
                    "module_importable", "matched_plugins", "warnings"):
            self.assertIn(key, report)

    def test_report_values_without_octane(self):
        report = detection.get_octane_status_report(None)
        self.assertIs(report["octane_detected"], False)
        self.assertIs(report["module_importable"], False)
        self.assertEqual(report["matched_plugins"], [])
        # Renderer state is undeterminable without a document.
        self.assertEqual(report["octane_renderer_active"], "unknown")
        self.assertTrue(report["warnings"])  # always carries limitations

    def test_format_status_report_is_a_string(self):
        report = detection.get_octane_status_report(None)
        text = detection.format_status_report(report)
        self.assertIsInstance(text, str)
        self.assertIn("Octane detected:", text)
        self.assertIn("no", text)  # detected -> "no"


if __name__ == "__main__":
    unittest.main()
