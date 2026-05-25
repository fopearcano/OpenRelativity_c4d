"""Tests for the safe icon loader (pure-Python parts; no Cinema 4D).

The path helpers must resolve relative to the plugin root without importing
``c4d``; the load/safe helpers must never raise and must return ``None`` when
Cinema 4D is unavailable (as in this test run). The module must not import ``c4d``
at top level.
"""

import os
import unittest

from openrelativity_c4d.c4d import icon_loader


class TestIconLoaderIsImportSafe(unittest.TestCase):
    def test_module_has_no_c4d_dependency(self):
        self.assertFalse(hasattr(icon_loader, "c4d"))


class TestPaths(unittest.TestCase):
    def test_plugin_root_points_at_package(self):
        root = icon_loader.get_plugin_root()
        self.assertTrue(os.path.isdir(root))
        self.assertEqual(os.path.basename(root), "openrelativity_c4d")
        self.assertTrue(os.path.isdir(os.path.join(root, "resources", "icons", "png")))

    def test_get_icon_path_finds_a_committed_icon(self):
        path = icon_loader.get_icon_path("icon_about")
        self.assertIsNotNone(path)
        self.assertTrue(os.path.isfile(path))
        self.assertTrue(path.endswith(os.path.join("png", "icon_about.png")))

    def test_get_icon_path_accepts_prefixless_and_suffixed_names(self):
        self.assertEqual(icon_loader.get_icon_path("setup_camera"),
                         icon_loader.get_icon_path("icon_setup_camera"))
        self.assertEqual(icon_loader.get_icon_path("icon_about.png"),
                         icon_loader.get_icon_path("icon_about"))

    def test_get_icon_path_missing_returns_none(self):
        self.assertIsNone(icon_loader.get_icon_path("icon_does_not_exist_zzz"))

    def test_get_icon_path_is_not_path_traversable(self):
        # Only a basename is used, so a traversal attempt cannot escape the dir.
        self.assertIsNone(icon_loader.get_icon_path("../../../../etc/passwd"))


class TestSafeLoading(unittest.TestCase):
    def setUp(self):
        icon_loader.reset_cache()

    def tearDown(self):
        icon_loader.reset_cache()

    def test_load_icon_bitmap_returns_none_without_c4d(self):
        # No Cinema 4D here -> None, never raises (even for an existing file).
        self.assertIsNone(icon_loader.load_icon_bitmap("icon_about"))

    def test_safe_icon_never_raises_and_is_none_without_c4d(self):
        self.assertIsNone(icon_loader.safe_icon("icon_about"))
        self.assertIsNone(icon_loader.safe_icon("icon_does_not_exist_zzz"))

    def test_safe_icon_is_cached(self):
        first = icon_loader.safe_icon("icon_about")
        second = icon_loader.safe_icon("icon_about")
        self.assertIs(first, second)

    def test_load_summary_tracks_requests(self):
        icon_loader.safe_icon("icon_about")
        icon_loader.safe_icon("icon_diagnostics")
        loaded, missing = icon_loader.get_load_summary()
        # Without Cinema 4D nothing actually loads, so both go to "missing".
        self.assertEqual(loaded, [])
        self.assertEqual(missing, ["icon_about", "icon_diagnostics"])
        self.assertIsInstance(icon_loader.format_load_summary(), str)


if __name__ == "__main__":
    unittest.main()
