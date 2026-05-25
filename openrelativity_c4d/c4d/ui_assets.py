"""Canonical UI asset registry: the command -> section/label/icon mapping.

Pure data (no ``import c4d``): the single, documented source of truth for which
commands exist, the section + leaf used to build their menu label
(:func:`openrelativity_c4d.constants.command_name`), and which icon each uses. It
mirrors docs/COMMAND_REFERENCE.md.

Consumed by the *UI Diagnostics* command (to list commands + expected icons) and
by ``tools/audit_ui_assets.py`` (to verify icon files exist and that the source
references stay consistent). Importing this pulls in no ``c4d`` and no Octane, so
it is unit-testable in plain Python.
"""

from collections import namedtuple

from .. import constants, ids

#: One command's UI metadata. ``const`` is the name of the ID constant in
#: :mod:`openrelativity_c4d.ids`; ``icon`` is the icon base name (see ICONS.md).
CommandSpec = namedtuple("CommandSpec", ("const", "section", "leaf", "icon"))

#: Every command, in a sensible menu order. Matches docs/COMMAND_REFERENCE.md.
COMMANDS = (
    CommandSpec("ID_ORC_CREATE_CONTROLLER_COMMAND", "Setup", "Create Controller", "icon_setup_controller"),
    CommandSpec("ID_ORC_SETUP_CAMERA_COMMAND", "Setup", "Setup Camera", "icon_setup_camera"),
    CommandSpec("ID_ORC_SETUP_OBJECTS_COMMAND", "Setup", "Setup Selected Objects", "icon_setup_objects"),
    CommandSpec("ID_ORC_SELECT_OBJECTS_COMMAND", "Setup", "Select Objects", "icon_setup_objects"),
    CommandSpec("ID_ORC_CREATE_TEST_SCENE_COMMAND", "Scene", "Create Test Scene", "icon_create_test_scene"),
    CommandSpec("ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND", "Preview", "Apply Doppler", "icon_doppler_preview"),
    CommandSpec("ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND", "Preview", "Apply Searchlight", "icon_searchlight_preview"),
    CommandSpec("ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND", "Preview", "Apply All Materials", "icon_all_previews"),
    CommandSpec("ID_ORC_APPLY_ALL_PREVIEWS_COMMAND", "Preview", "Apply All", "icon_all_previews"),
    CommandSpec("ID_ORC_CLEAR_PREVIEW_COMMAND", "Preview", "Clear Generated Preview Materials", "icon_lorentz_remove"),
    CommandSpec("ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND", "Preview", "Create Lorentz Copies", "icon_lorentz_create"),
    CommandSpec("ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND", "Preview", "Remove Lorentz Copies", "icon_lorentz_remove"),
    CommandSpec("ID_ORC_OCTANE_STATUS_COMMAND", "Octane", "Status", "icon_octane_status"),
    CommandSpec("ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND", "Octane", "Apply Compatible Preview", "icon_octane_status"),
    CommandSpec("ID_ORC_SHOW_AOV_PLAN_COMMAND", "Octane", "Show AOV Plan", "icon_aov_plan"),
    CommandSpec("ID_ORC_OCTANE_DIAGNOSTICS_COMMAND", "Octane", "Diagnostics", "icon_diagnostics"),
    CommandSpec("ID_ORC_EXPORT_METADATA_COMMAND", "Export", "Metadata JSON", "icon_export_metadata"),
    CommandSpec("ID_ORC_EXPORT_OSL_CAMERA_COMMAND", "Experimental", "Export OSL Camera", "icon_export_osl"),
    CommandSpec("ID_ORC_UI_DIAGNOSTICS_COMMAND", "Diagnostics", "UI Diagnostics", "icon_diagnostics"),
    CommandSpec("ID_ORC_ABOUT_COMMAND", "Help", "About", "icon_about"),
    CommandSpec("ID_ORC_CONTROL_PANEL_COMMAND", "Help", "Control Panel", "icon_control_panel"),
)


def menu_label(spec):
    """Return the full grouped menu label for ``spec``."""
    return constants.command_name(spec.section, spec.leaf)


def command_id(spec):
    """Return the integer plugin ID for ``spec`` (or ``None`` if undefined)."""
    return getattr(ids, spec.const, None)


def expected_icon_names():
    """Return the de-duplicated list of icon base names every command needs."""
    names = []
    for spec in COMMANDS:
        if spec.icon and spec.icon not in names:
            names.append(spec.icon)
    return names


def command_id_constants():
    """Return the set of ``ID_ORC_*_COMMAND`` constant names this registry covers."""
    return {spec.const for spec in COMMANDS}
