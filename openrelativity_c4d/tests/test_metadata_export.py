"""Tests for the relativity metadata export.

Run in plain Python (no Cinema 4D). They cover the schema skeleton, JSON
serialization, the sanitizer, and file export with ``doc=None`` - the c4d-backed
collection path is exercised manually in Cinema 4D.
"""

import json
import os
import tempfile
import unittest

from openrelativity_c4d.export import metadata_export


class TestMetadataExportSafe(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        self.assertFalse(hasattr(metadata_export, "c4d"))

    def test_collect_skeleton_without_doc(self):
        md = metadata_export.collect_metadata(None)
        self.assertEqual(md["schema"], metadata_export.SCHEMA_NAME)
        self.assertEqual(md["schema_version"], metadata_export.SCHEMA_VERSION)
        self.assertIn("plugin_version", md)
        self.assertIs(md["controller"]["present"], False)
        self.assertIs(md["camera"]["present"], False)
        self.assertEqual(md["objects"], [])
        self.assertTrue(md["approximation_notes"])

    def test_to_json_round_trips(self):
        md = metadata_export.collect_metadata(None)
        text = metadata_export.to_json(md)
        self.assertIsInstance(text, str)
        parsed = json.loads(text)
        self.assertEqual(parsed["schema"], metadata_export.SCHEMA_NAME)

    def test_sanitize_handles_tuples_and_unknowns(self):
        class Weird:
            def __str__(self):
                return "weird"

        out = metadata_export._sanitize(
            {"v": (1.0, 2.0, 3.0), "x": Weird(), "n": None, "b": True})
        self.assertEqual(out["v"], [1.0, 2.0, 3.0])
        self.assertEqual(out["x"], "weird")
        self.assertIsNone(out["n"])
        self.assertIs(out["b"], True)

    def test_default_filename_is_json(self):
        name = metadata_export.default_filename(None)
        self.assertTrue(name.endswith(".json"))
        self.assertIn("ORC_metadata", name)

    def test_export_writes_valid_json(self):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, metadata_export.default_filename(None))
        result = metadata_export.export_metadata_json(None, path)
        self.assertTrue(result["ok"])
        self.assertEqual(result["object_count"], 0)
        with open(path) as handle:
            parsed = json.load(handle)
        self.assertEqual(parsed["schema"], metadata_export.SCHEMA_NAME)

    def test_export_reports_error_on_bad_path(self):
        result = metadata_export.export_metadata_json(
            None, os.path.join("no_such_dir_xyz", "x", "out.json"))
        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
