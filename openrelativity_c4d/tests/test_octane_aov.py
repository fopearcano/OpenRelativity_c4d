"""Tests for the Octane AOV scaffolding.

Run in plain Python (no Octane, no Cinema 4D). They verify the AOV plan is
well-formed and that nothing claims unsupported capabilities or raises.
"""

import unittest

from openrelativity_c4d.octane import aov_adapter

EXPECTED_AOV_NAMES = {
    "ORC_DopplerFactor",
    "ORC_Beta",
    "ORC_Searchlight",
    "ORC_ObjectVelocity",
    "ORC_RelativityMask",
}


class TestAOVPlan(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        self.assertFalse(hasattr(aov_adapter, "c4d"))

    def test_plan_lists_the_expected_aovs(self):
        plan = aov_adapter.get_relativity_aov_plan()
        names = {spec.name for spec in plan["aovs"]}
        self.assertEqual(names, EXPECTED_AOV_NAMES)

    def test_plan_does_not_overclaim(self):
        plan = aov_adapter.get_relativity_aov_plan()
        self.assertIs(plan["automatic_creation_supported"], False)
        self.assertTrue(plan["reason"])
        self.assertTrue(plan["missing"])
        self.assertTrue(plan["manual_setup"])

    def test_aov_creation_unsupported_without_octane(self):
        supported, reason = aov_adapter.aov_creation_supported(None)
        self.assertIs(supported, False)
        self.assertTrue(reason)

    def test_create_aovs_is_safe_no_op(self):
        result = aov_adapter.create_relativity_aovs(None)
        self.assertIs(result["ok"], False)
        self.assertEqual(result["created"], [])

    def test_detect_render_settings_safe_without_c4d(self):
        info = aov_adapter.detect_render_settings(None)
        self.assertIn("octane_detected", info)
        self.assertIn("octane_renderer_active", info)
        # No Octane / no Cinema 4D here.
        self.assertIs(info["octane_detected"], False)

    def test_format_aov_plan_is_a_string(self):
        plan = aov_adapter.get_relativity_aov_plan()
        text = aov_adapter.format_aov_plan(plan, aov_adapter.detect_render_settings(None))
        self.assertIsInstance(text, str)
        for name in EXPECTED_AOV_NAMES:
            self.assertIn(name, text)
        self.assertIn("NOT supported", text)


if __name__ == "__main__":
    unittest.main()
