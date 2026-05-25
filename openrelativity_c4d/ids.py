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

# --- Commands (active in this skeleton) -------------------------------------
COMMAND_ABOUT = 1000001  # PLACEHOLDER - replace with a registered Plugin Cafe ID

# --- Dialog layout IDs ------------------------------------------------------
DIALOG_ABOUT = 1000002  # PLACEHOLDER - replace with a registered Plugin Cafe ID

# --- Reserved for later phases (NOT registered/used yet) --------------------
# Declared now so the numbers are tracked in one place; wiring comes later.
SCENEHOOK_RELATIVITY = 1000003     # PLACEHOLDER - Relativity Scene Controller
TAG_RELATIVISTIC_CAMERA = 1000004  # PLACEHOLDER - Relativistic Camera Tag
TAG_RELATIVISTIC_OBJECT = 1000005  # PLACEHOLDER - Relativistic Object Tag
OBJECT_LORENTZ_DEFORMER = 1000006  # PLACEHOLDER - Lorentz deformer / bake
COMMAND_SCENE_CONTROLLER = 1000007 # PLACEHOLDER - create/sync Scene Controller


def all_ids():
    """Return ``{name: id}`` for every declared ID. Useful for collision checks."""
    return {
        name: value
        for name, value in globals().items()
        if name.isupper() and isinstance(value, int)
    }
