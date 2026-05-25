"""Tests for the Octane diagnostics command's safe behaviour.

These run in plain Python (no Octane, no Cinema 4D). They verify the diagnostics
collector returns a structured report and never raises when Octane / Cinema 4D
are unavailable, and that it never imports ``c4d`` at module scope.
"""

import unittest

from openrelativity_c4d.octane import diagnostics


class TestOctaneDiagnosticsSafe(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        self.assertFalse(hasattr(diagnostics, "c4d"))

    def test_collect_returns_expected_keys(self):
        data = diagnostics.collect_diagnostics(None)
        self.assertIsInstance(data, dict)
        for key in ("octane_module_importable", "plugins", "material_type_id",
                    "material_parameters", "notes"):
            self.assertIn(key, data)

    def test_collect_values_without_octane(self):
        data = diagnostics.collect_diagnostics(None)
        self.assertIs(data["octane_module_importable"], False)
        self.assertEqual(data["plugins"], [])
        self.assertIsNone(data["material_type_id"])
        self.assertEqual(data["material_parameters"], [])
        self.assertTrue(data["notes"])  # always carries read-only guidance

    def test_format_is_a_string(self):
        data = diagnostics.collect_diagnostics(None)
        text = diagnostics.format_diagnostics(data)
        self.assertIsInstance(text, str)
        self.assertIn("Octane module importable:", text)
        self.assertIn("none detected", text)


if __name__ == "__main__":
    unittest.main()
