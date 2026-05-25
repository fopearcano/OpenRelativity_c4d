"""Cinema 4D plugin IDs.

==============================================================================
!!! PLACEHOLDER IDS - DEVELOPMENT ONLY - DO NOT SHIP !!!
==============================================================================

Every Cinema 4D plugin element (command, tag, object, scene hook, dialog layout)
needs a **globally unique** integer ID. Real IDs are obtained, free of charge,
from Maxon's Plugin Cafe / developer portal:

    https://plugincafe.maxon.net/   (and https://developers.maxon.net/)

The IDs below are temporary placeholders drawn from the 1000001-1000010 range
that Maxon reserves for **local testing only**. They are guaranteed to collide
with other developers' test plugins and MUST NOT be used in any public release.

>>> ACTION REQUIRED before any release / distribution:
>>>   1. Register one unique ID per element at Plugin Cafe.
>>>   2. Replace each value below with its registered ID.
>>>   3. Remove this warning once all IDs are real.

Shipping with these placeholders can break other plugins and corrupt user
scenes that reference the wrong ID.
"""

# --- Commands (active) ------------------------------------------------------
COMMAND_ABOUT = 1000001             # PLACEHOLDER - replace with a registered ID
COMMAND_CREATE_CONTROLLER = 1000007 # PLACEHOLDER - "Create Relativity Controller"
COMMAND_SETUP_CAMERA = 1000008      # PLACEHOLDER - "Setup Relativistic Camera"
COMMAND_SETUP_OBJECTS = 1000009     # PLACEHOLDER - "Setup Selected Relativistic Objects"
COMMAND_SELECT_OBJECTS = 1000010    # PLACEHOLDER - "Select Relativistic Objects"

# !!! The IDs below are PAST Maxon's 1000001-1000010 test range. They may
# collide with REAL registered plugins even during local testing. They are only
# acceptable as a temporary stop-gap and MUST be replaced with registered Plugin
# Cafe IDs before the plugin is run alongside third-party plugins or shipped.
COMMAND_APPLY_DOPPLER = 1000011     # PLACEHOLDER (out of test range!) - "Apply Doppler Material Preview"
COMMAND_CLEAR_PREVIEW = 1000012     # PLACEHOLDER (out of test range!) - "Clear Material Preview"
COMMAND_APPLY_SEARCHLIGHT = 1000013 # PLACEHOLDER (out of test range!) - "Apply Searchlight Preview"
COMMAND_APPLY_RELATIVITY_PREVIEW = 1000014  # PLACEHOLDER (out of test range!) - "Apply Relativity Material Preview"
COMMAND_CREATE_LORENTZ = 1000015    # PLACEHOLDER (out of test range!) - "Create Lorentz Preview Copies"
COMMAND_REMOVE_LORENTZ = 1000016    # PLACEHOLDER (out of test range!) - "Remove Lorentz Preview Copies"
COMMAND_CREATE_TEST_SCENE = 1000017 # PLACEHOLDER (out of test range!) - "Create Test Scene"
COMMAND_APPLY_ALL = 1000018         # PLACEHOLDER (out of test range!) - "Apply All Previews"
COMMAND_OCTANE_STATUS = 1000019     # PLACEHOLDER (out of test range!) - "Octane Status"
COMMAND_APPLY_OCTANE_MATERIAL = 1000020  # PLACEHOLDER (out of test range!) - "Apply Octane-Compatible Material Preview"
COMMAND_SHOW_AOV_PLAN = 1000021     # PLACEHOLDER (out of test range!) - "Show AOV Plan"
COMMAND_EXPORT_OSL_CAMERA = 1000022  # PLACEHOLDER (out of test range!) - "Export Experimental OSL Camera"
COMMAND_EXPORT_METADATA = 1000023   # PLACEHOLDER (out of test range!) - "Export Relativity Metadata JSON"
COMMAND_CONTROL_PANEL = 1000024     # PLACEHOLDER (out of test range!) - "Control Panel"
COMMAND_OCTANE_DIAGNOSTICS = 1000026  # PLACEHOLDER (out of test range!) - "Octane Diagnostics"

# --- Dialog layout IDs (additional) -----------------------------------------
DIALOG_CONTROL_PANEL = 1000025      # PLACEHOLDER (out of test range!) - Control Panel async dialog

# --- Dialog layout IDs ------------------------------------------------------
DIALOG_ABOUT = 1000002  # PLACEHOLDER - replace with a registered Plugin Cafe ID

# --- Reserved for later phases (NOT registered/used yet) --------------------
# Declared now so the numbers are tracked in one place; wiring comes later.
# Note: the Relativity Controller is currently a Null + User Data (see
# c4d/scene_controller.py); its fields are addressed by name, so they need no
# registered IDs. SCENEHOOK_RELATIVITY is reserved for a future ObjectData/hook.
SCENEHOOK_RELATIVITY = 1000003     # PLACEHOLDER - Relativity Scene Controller (future)
TAG_RELATIVISTIC_CAMERA = 1000004  # PLACEHOLDER - Relativistic Camera Tag
TAG_RELATIVISTIC_OBJECT = 1000005  # PLACEHOLDER - Relativistic Object Tag
OBJECT_LORENTZ_DEFORMER = 1000006  # PLACEHOLDER - Lorentz deformer / bake


def all_ids():
    """Return ``{name: id}`` for every declared ID. Useful for collision checks."""
    return {
        name: value
        for name, value in globals().items()
        if name.isupper() and isinstance(value, int)
    }
