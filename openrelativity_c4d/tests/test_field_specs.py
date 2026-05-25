"""Tests for the declarative field schema (pure; no Cinema 4D).

The schema (`c4d.field_specs`) is the canonical parameter definition the
TagData/ObjectData migration will iterate. These tests guard its consistency.
"""

import unittest

from openrelativity_c4d.c4d import field_specs


class TestFieldSpecs(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        self.assertFalse(hasattr(field_specs, "c4d"))

    def test_three_entities(self):
        self.assertEqual(set(field_specs.ENTITIES), {"controller", "camera", "object"})

    def test_validate_is_clean(self):
        self.assertEqual(field_specs.validate(), [])

    def test_field_names_unique_per_entity(self):
        for key in field_specs.ENTITIES:
            names = field_specs.field_names(key)
            self.assertEqual(len(names), len(set(names)), key)

    def test_groups_are_valid(self):
        for entity in field_specs.ENTITIES.values():
            for field in entity.fields:
                self.assertIn(field.group, entity.groups)

    def test_known_fields_and_defaults(self):
        self.assertIn("Artificial Speed of Light", field_specs.field_names("controller"))
        self.assertIn("Observer Velocity", field_specs.field_names("camera"))
        for axis in ("Velocity X", "Velocity Y", "Velocity Z"):
            self.assertIn(axis, field_specs.field_names("object"))
        self.assertIs(field_specs.defaults("controller")["Enabled"], True)
        self.assertEqual(field_specs.defaults("controller")["Artificial Speed of Light"], 1000.0)
        self.assertEqual(field_specs.defaults("object")["Object Beta"], 0.0)

    def test_cycle_field_default_in_range(self):
        controller = field_specs.ENTITIES["controller"]
        preview = next(f for f in controller.fields if f.name == "Preview Mode")
        self.assertEqual(preview.kind, field_specs.KIND_CYCLE)
        self.assertTrue(0 <= preview.default < len(preview.cycle))

    def test_vector_default_is_tuple(self):
        velocity = next(f for f in field_specs.ENTITIES["camera"].fields
                        if f.name == "Observer Velocity")
        self.assertEqual(velocity.kind, field_specs.KIND_VECTOR)
        self.assertEqual(velocity.default, (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
