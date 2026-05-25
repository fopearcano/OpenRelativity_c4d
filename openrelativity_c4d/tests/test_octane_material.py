"""Tests for the Octane material adapter's safe / fallback behaviour.

These run in plain Python (no Octane, no Cinema 4D). They verify the adapter
reports a structured result and never raises when Octane is unavailable.
"""

import unittest

from openrelativity_c4d.octane import material_adapter


class TestOctaneMaterialAdapterSafe(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        self.assertFalse(hasattr(material_adapter, "c4d"))

    def test_unavailable_returns_structured_result(self):
        # No Octane here -> ok False, method "unavailable", never raises.
        result = material_adapter.create_or_update_octane_doppler_material(
            None, None, (1.0, 0.0, 0.0), 2.0)
        self.assertIsInstance(result, dict)
        self.assertIs(result["ok"], False)
        self.assertEqual(result["method"], material_adapter.METHOD_UNAVAILABLE)
        self.assertTrue(result["warnings"])
        self.assertIn("missing", result)

    def test_required_info_is_documented(self):
        info = material_adapter.required_octane_material_info()
        self.assertTrue(info)
        self.assertTrue(all(isinstance(item, str) for item in info))


if __name__ == "__main__":
    unittest.main()
