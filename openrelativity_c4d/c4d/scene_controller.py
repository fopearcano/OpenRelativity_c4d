"""Relativity Scene Controller - a Null object carrying organized User Data.

Phase 1 deliberately avoids a full ``ObjectData`` plugin (which needs description
resources). Instead the controller is an ordinary Cinema 4D **Null** named
``ORC_Relativity_Controller`` with structured **User Data**. This is robust, needs
no resource files, and is easy for artists to inspect in the Attribute Manager.

This module owns:

* the controller name and its User Data **field names** (the single source of
  truth - the rest of the plugin refers to these constants, never raw strings),
* creation of the Null + User Data with safe defaults,
* lookup of an existing controller in a document,
* clean read/write helpers (:func:`get_value` / :func:`set_value` /
  :func:`read_state`).

The low-level User Data plumbing lives in :mod:`openrelativity_c4d.c4d.userdata`
(shared with the camera and future tags). Fields are addressed **by name**, so
the accessors keep working even if the layout/order changes later.

``import c4d`` here resolves to Cinema 4D's module (absolute import), not the
``openrelativity_c4d.c4d`` sub-package.
"""

import c4d

from ..logging_utils import get_logger
from . import userdata

log = get_logger("scene_controller")

#: The Null's name; used to find the single controller in a scene.
CONTROLLER_NAME = "ORC_Relativity_Controller"

# --- User Data field names (the central identifiers for the controller) -----
FIELD_ENABLED = "Enabled"
FIELD_SPEED_OF_LIGHT = "Artificial Speed of Light"
FIELD_BETA_OVERRIDE = "Global Beta Override"
FIELD_DOPPLER_STRENGTH = "Doppler Strength"
FIELD_SEARCHLIGHT_STRENGTH = "Searchlight Strength"
FIELD_LORENTZ_STRENGTH = "Lorentz Deformation Strength"
FIELD_PREVIEW_MODE = "Preview Mode"
FIELD_HIDE_ORIGINALS_LORENTZ = "Hide Originals (Lorentz Preview)"
FIELD_OCTANE_ENABLED = "Octane Adapter Enabled"
FIELD_BAKE_ENABLED = "Bake Mode Enabled"

#: Preview-mode cycle labels (index order matters; index is the stored value).
PREVIEW_MODES = ["Off", "Doppler", "Searchlight", "Doppler + Searchlight"]
PREVIEW_MODE_DEFAULT = 3  # "Doppler + Searchlight"

#: Safe default values, keyed by field name.
DEFAULTS = {
    FIELD_ENABLED: True,
    FIELD_SPEED_OF_LIGHT: 1000.0,
    FIELD_BETA_OVERRIDE: 0.0,
    FIELD_DOPPLER_STRENGTH: 1.0,
    FIELD_SEARCHLIGHT_STRENGTH: 1.0,
    FIELD_LORENTZ_STRENGTH: 1.0,
    FIELD_PREVIEW_MODE: PREVIEW_MODE_DEFAULT,
    FIELD_HIDE_ORIGINALS_LORENTZ: True,
    FIELD_OCTANE_ENABLED: False,
    FIELD_BAKE_ENABLED: False,
}


def _build_user_data(null):
    """Attach the organized User Data fields with safe defaults."""
    g_main = userdata.add_group(null, "Relativity")
    userdata.add_bool(null, FIELD_ENABLED, DEFAULTS[FIELD_ENABLED], g_main)
    userdata.add_real(null, FIELD_SPEED_OF_LIGHT, DEFAULTS[FIELD_SPEED_OF_LIGHT],
                      g_main, min_val=0.001, step=1.0)
    userdata.add_real(null, FIELD_BETA_OVERRIDE, DEFAULTS[FIELD_BETA_OVERRIDE],
                      g_main, min_val=0.0, max_val=0.999, step=0.001,
                      unit=c4d.DESC_UNIT_PERCENT)

    g_fx = userdata.add_group(null, "Visual Effects")
    for field in (FIELD_DOPPLER_STRENGTH, FIELD_SEARCHLIGHT_STRENGTH,
                  FIELD_LORENTZ_STRENGTH):
        userdata.add_real(null, field, DEFAULTS[field], g_fx,
                          min_val=0.0, max_val=1.0, step=0.01,
                          unit=c4d.DESC_UNIT_PERCENT)
    userdata.add_cycle(null, FIELD_PREVIEW_MODE, PREVIEW_MODES,
                       DEFAULTS[FIELD_PREVIEW_MODE], g_fx)
    userdata.add_bool(null, FIELD_HIDE_ORIGINALS_LORENTZ,
                      DEFAULTS[FIELD_HIDE_ORIGINALS_LORENTZ], g_fx)

    g_int = userdata.add_group(null, "Integration")
    userdata.add_bool(null, FIELD_OCTANE_ENABLED, DEFAULTS[FIELD_OCTANE_ENABLED], g_int)
    userdata.add_bool(null, FIELD_BAKE_ENABLED, DEFAULTS[FIELD_BAKE_ENABLED], g_int)


# --- Lookup / creation -------------------------------------------------------
def _iter_objects(op):
    """Depth-first iterate an object and its siblings/children."""
    while op:
        yield op
        for child in _iter_objects(op.GetDown()):
            yield child
        op = op.GetNext()


def find_controller(doc):
    """Return the controller Null in ``doc`` (by name + type), or ``None``."""
    if doc is None:
        return None
    for op in _iter_objects(doc.GetFirstObject()):
        if op.GetName() == CONTROLLER_NAME and op.GetType() == c4d.Onull:
            return op
    return None


def create_controller(doc):
    """Create the controller Null with User Data and insert it (undo-able).

    Returns the created object, or ``None`` on failure.
    """
    try:
        null = c4d.BaseObject(c4d.Onull)
        if null is None:
            log.error("Could not allocate a Null object.")
            return None
        null.SetName(CONTROLLER_NAME)
        _build_user_data(null)
    except Exception:  # noqa: BLE001
        log.exception("Failed to build the Relativity Controller.")
        return None

    doc.StartUndo()
    doc.InsertObject(null)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, null)
    doc.EndUndo()
    doc.SetActiveObject(null)
    c4d.EventAdd()
    log.info("Created %s with default User Data.", CONTROLLER_NAME)
    return null


def find_or_create(doc):
    """Return ``(controller, created)`` - find the controller or create it."""
    existing = find_controller(doc)
    if existing is not None:
        return existing, False
    return create_controller(doc), True


# --- Read / write helpers (delegate to the shared, name-based accessors) -----
def get_value(controller, field_name, default=None):
    """Read a controller field by name. Returns ``default`` if missing."""
    if controller is None:
        return default
    return userdata.get_value(controller, field_name, default)


def set_value(controller, field_name, value):
    """Write a controller field by name. Returns ``True`` on success."""
    if controller is None:
        return False
    if not userdata.set_value(controller, field_name, value):
        log.warning("Controller has no field %r.", field_name)
        return False
    return True


def read_state(controller):
    """Return all controller fields as a ``{field_name: value}`` dict.

    Missing fields fall back to their default, so callers always get a complete
    dict even on a partially-built controller.
    """
    return {name: get_value(controller, name, DEFAULTS.get(name))
            for name in DEFAULTS}
