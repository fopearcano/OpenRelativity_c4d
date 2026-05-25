"""Tests for the experimental OSL camera generator.

Run in plain Python (no Octane, no Cinema 4D). They verify the generated shader
text is well-formed enough, exposes the required parameters, stays in sync with
the committed example file, and that export writes a file without touching c4d.
"""

import os
import tempfile
import unittest

from openrelativity_c4d.octane import osl_camera

REQUIRED_PARAMS = (
    "beta",
    "velocity_dir",
    "aberration_strength",
    "doppler_strength",
    "fov_scale",
)


class TestOSLCameraGenerator(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        self.assertFalse(hasattr(osl_camera, "c4d"))

    def test_source_marked_experimental(self):
        src = osl_camera.get_osl_source()
        self.assertIn("EXPERIMENTAL", src)
        self.assertIn("shader relativity_camera_experimental", src)

    def test_source_declares_required_parameters(self):
        src = osl_camera.get_osl_source()
        for name in REQUIRED_PARAMS:
            self.assertIn(name, src)

    def test_parameters_table_matches_required(self):
        names = {p[0] for p in osl_camera.PARAMETERS}
        self.assertEqual(names, set(REQUIRED_PARAMS))

    def test_source_matches_committed_example(self):
        # this file: <repo>/openrelativity_c4d/tests/test_osl_camera.py
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
        example = os.path.join(repo_root, "examples", "osl",
                               osl_camera.OSL_FILENAME)
        if not os.path.exists(example):
            self.skipTest("example OSL file not present")
        with open(example) as handle:
            self.assertEqual(handle.read(), osl_camera.get_osl_source())

    def test_export_writes_file(self):
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, osl_camera.OSL_FILENAME)
        result = osl_camera.export_osl_camera(path)
        self.assertTrue(result["ok"])
        self.assertIsNone(result["error"])
        with open(path) as handle:
            self.assertEqual(handle.read(), osl_camera.get_osl_source())

    def test_export_reports_error_on_bad_path(self):
        result = osl_camera.export_osl_camera(
            os.path.join("no_such_dir_xyz", "sub", osl_camera.OSL_FILENAME))
        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
