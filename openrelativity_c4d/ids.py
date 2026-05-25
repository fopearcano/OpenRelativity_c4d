"""Cinema 4D plugin IDs - the SINGLE source of truth for this plugin.

==============================================================================
!!! TEMPORARY PRIVATE PROTOTYPE IDS - DO NOT SHIP AS-IS !!!
==============================================================================

Every Cinema 4D plugin element (command, dialog layout, tag, object, scene hook)
needs a **globally unique** 32-bit integer ID, passed to the ``c4d.plugins``
registration functions. If two installed plugins claim the same ID, Cinema 4D
loads only ONE of them at startup - so a duplicated or copied-from-sample ID here
can silently block another plugin (and vice versa). That is the exact failure
this file is structured to avoid.

The IDs below are **temporary private prototype IDs**, derived as
``ORC_ID_BASE + n``. They are NOT obtained from Maxon's Plugin Cafe and are NOT
guaranteed globally unique; they only move this plugin OFF the heavily-reused
``1000001-1000010`` test range that sample/tutorial code sits on.

>>> ACTION REQUIRED before any public release / distribution:
>>>   1. Register one unique ID per element at Plugin Cafe
>>>      (https://plugincafe.maxon.net/ , https://developers.maxon.net/).
>>>   2. Either set ``ORC_ID_BASE`` to your first registered ID and register a
>>>      contiguous block, or give each constant its own registered ID.
>>>   3. Remove this warning once all IDs are real.

If another LOCAL plugin appears blocked at Cinema 4D startup, change
``ORC_ID_BASE`` below to a different high number and restart Cinema 4D: that
relocates this whole block at once. See docs/DEVELOPER_NOTES.md -> "Plugin IDs".
"""

# ---------------------------------------------------------------------------
# Prototype base ID.
#
# TEMPORARY PRIVATE PROTOTYPE IDS. Replace with official Plugin Cafe IDs before
# release.
#
# This value is deliberately NOT copied from any Maxon/SDK example, forum
# snippet, or other plugin: it is anchored on the speed of light in m/s
# (299,792,458), a distinctive constant that suits this project and sits far from
# the reused 1000001-1000010 test range and the usual sample IDs. It is still a
# guess, not a registered ID. Change ONLY this number to move every ID below in
# lockstep if it ever collides locally.
# ---------------------------------------------------------------------------
ORC_ID_BASE = 299792458

# --- Command plugins (CommandData; registered in c4d/plugin_register.py) ----
ID_ORC_ABOUT_COMMAND = ORC_ID_BASE + 1
ID_ORC_CONTROL_PANEL_COMMAND = ORC_ID_BASE + 2
ID_ORC_CREATE_CONTROLLER_COMMAND = ORC_ID_BASE + 3
ID_ORC_SETUP_CAMERA_COMMAND = ORC_ID_BASE + 4
ID_ORC_SETUP_OBJECTS_COMMAND = ORC_ID_BASE + 5
ID_ORC_SELECT_OBJECTS_COMMAND = ORC_ID_BASE + 6
ID_ORC_CREATE_TEST_SCENE_COMMAND = ORC_ID_BASE + 7
ID_ORC_APPLY_DOPPLER_PREVIEW_COMMAND = ORC_ID_BASE + 8
ID_ORC_APPLY_SEARCHLIGHT_PREVIEW_COMMAND = ORC_ID_BASE + 9
ID_ORC_APPLY_RELATIVITY_PREVIEW_COMMAND = ORC_ID_BASE + 10
ID_ORC_CLEAR_PREVIEW_COMMAND = ORC_ID_BASE + 11
ID_ORC_APPLY_ALL_PREVIEWS_COMMAND = ORC_ID_BASE + 12
ID_ORC_CREATE_LORENTZ_PREVIEWS_COMMAND = ORC_ID_BASE + 13
ID_ORC_REMOVE_LORENTZ_PREVIEWS_COMMAND = ORC_ID_BASE + 14
ID_ORC_OCTANE_STATUS_COMMAND = ORC_ID_BASE + 15
ID_ORC_OCTANE_DIAGNOSTICS_COMMAND = ORC_ID_BASE + 16
ID_ORC_APPLY_OCTANE_MATERIAL_COMMAND = ORC_ID_BASE + 17
ID_ORC_SHOW_AOV_PLAN_COMMAND = ORC_ID_BASE + 18
ID_ORC_EXPORT_OSL_CAMERA_COMMAND = ORC_ID_BASE + 19
ID_ORC_EXPORT_METADATA_COMMAND = ORC_ID_BASE + 20
ID_ORC_UI_DIAGNOSTICS_COMMAND = ORC_ID_BASE + 27  # (offset continues past the reserved block)

# --- Dialog layout IDs (GeDialog .Open/.Restore pluginid) -------------------
ID_ORC_ABOUT_DIALOG = ORC_ID_BASE + 21
ID_ORC_CONTROL_PANEL_DIALOG = ORC_ID_BASE + 22
ID_ORC_UI_DIAGNOSTICS_DIALOG = ORC_ID_BASE + 28

# --- Reserved for later phases (declared now; NOT registered/used yet) ------
# Tracked here so every number lives in one place; wiring comes later. The
# Relativity Controller is currently a Null + User Data (see
# c4d/scene_controller.py) addressed by field name, so it needs no registered ID.
ID_ORC_RELATIVITY_SCENEHOOK = ORC_ID_BASE + 23
ID_ORC_RELATIVISTIC_CAMERA_TAG = ORC_ID_BASE + 24
ID_ORC_RELATIVISTIC_OBJECT_TAG = ORC_ID_BASE + 25
ID_ORC_LORENTZ_DEFORMER_OBJECT = ORC_ID_BASE + 26


def all_ids():
    """Return ``{name: id}`` for every declared ``ID_ORC_*`` constant.

    Excludes ``ORC_ID_BASE`` itself. Used by ``tools/audit_plugin_ids.py`` for the
    uniqueness / sample-collision self-check.
    """
    return {
        name: value
        for name, value in globals().items()
        if name.startswith("ID_ORC_") and isinstance(value, int)
    }
