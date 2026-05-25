"""Tests for the canonical UI asset registry (pure; no Cinema 4D).

Guards that the command<->icon<->label registry stays consistent with the plugin
IDs, so a command added to ``ids.py`` (or the registry) cannot silently drift.
The module must not import ``c4d`` at top level.
"""

import unittest

from openrelativity_c4d import ids
from openrelativity_c4d.c4d import ui_assets


class TestModuleIsImportSafe(unittest.TestCase):
    def test_no_c4d_dependency(self):
        self.assertFalse(hasattr(ui_assets, "c4d"))


class TestRegistry(unittest.TestCase):
    def test_commands_present(self):
        self.assertTrue(ui_assets.COMMANDS)

    def test_every_command_resolves_to_an_id(self):
        unresolved = [s.const for s in ui_assets.COMMANDS
                      if ui_assets.command_id(s) is None]
        self.assertEqual(unresolved, [])

    def test_registry_matches_ids_command_constants(self):
        ids_cmd = {n for n in ids.all_ids() if n.endswith("_COMMAND")}
        self.assertEqual(ui_assets.command_id_constants(), ids_cmd)

    def test_every_command_has_an_icon(self):
        for spec in ui_assets.COMMANDS:
            self.assertTrue(spec.icon, spec.const)

    def test_expected_icons_are_named_and_unique(self):
        names = ui_assets.expected_icon_names()
        self.assertTrue(names)
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(n.startswith("icon_") for n in names))

    def test_menu_label_format(self):
        label = ui_assets.menu_label(ui_assets.COMMANDS[0])
        self.assertTrue(label.startswith("OpenRelativity C4D / "))
        self.assertEqual(label.count(" / "), 2)


if __name__ == "__main__":
    unittest.main()
