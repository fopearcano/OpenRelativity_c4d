"""Relativistic Object setup - scene objects carrying organized User Data.

Like the controller and camera, a "relativistic object" is (for now) an ordinary
Cinema 4D object with structured **User Data** rather than a ``TagData`` plugin.
The "Setup Selected Relativistic Objects" command adds this data to each eligible
selected object; "Select Relativistic Objects" re-selects every object that has
it.

This module owns the object User Data field names + defaults and the lookup
utilities. It depends only on the shared :mod:`openrelativity_c4d.c4d.userdata`
plumbing (no controller/camera coupling). This step is **metadata only** - no
geometry is deformed and no material is changed.

``import c4d`` here resolves to Cinema 4D's module (absolute import).
"""

import c4d

from ..logging_utils import get_logger
from . import userdata

log = get_logger("object_tools")

# --- User Data field names (central identifiers for relativistic objects) ---
FIELD_ORC_ENABLED = "ORC Object Enabled"
FIELD_OBJECT_BETA = "Object Beta"
FIELD_VELOCITY_X = "Velocity X"
FIELD_VELOCITY_Y = "Velocity Y"
FIELD_VELOCITY_Z = "Velocity Z"
FIELD_USE_CAMERA_DIRECTION = "Use Camera Relative Direction"
FIELD_DOPPLER_PREVIEW = "Doppler Material Preview"
FIELD_SEARCHLIGHT_PREVIEW = "Searchlight Material Preview"
FIELD_LORENTZ_PREVIEW = "Lorentz Deformation Preview"
FIELD_BAKE_ELIGIBLE = "Bake Eligible"
FIELD_OCTANE_MATERIAL_SYNC = "Octane Material Sync Enabled"

#: The three velocity component fields, in order.
VELOCITY_FIELDS = (FIELD_VELOCITY_X, FIELD_VELOCITY_Y, FIELD_VELOCITY_Z)

#: Safe defaults, keyed by field name.
DEFAULTS = {
    FIELD_ORC_ENABLED: True,
    FIELD_OBJECT_BETA: 0.0,
    FIELD_VELOCITY_X: 0.0,
    FIELD_VELOCITY_Y: 0.0,
    FIELD_VELOCITY_Z: 0.0,
    FIELD_USE_CAMERA_DIRECTION: True,
    FIELD_DOPPLER_PREVIEW: True,
    FIELD_SEARCHLIGHT_PREVIEW: True,
    FIELD_LORENTZ_PREVIEW: True,
    FIELD_BAKE_ELIGIBLE: False,
    FIELD_OCTANE_MATERIAL_SYNC: False,
}


def _build_user_data(obj):
    """Attach the organized object User Data with safe defaults."""
    g_obj = userdata.add_group(obj, "Relativistic Object")
    userdata.add_bool(obj, FIELD_ORC_ENABLED, DEFAULTS[FIELD_ORC_ENABLED], g_obj)
    userdata.add_real(obj, FIELD_OBJECT_BETA, DEFAULTS[FIELD_OBJECT_BETA], g_obj,
                      min_val=0.0, max_val=0.999, step=0.001,
                      unit=c4d.DESC_UNIT_PERCENT)
    for field in VELOCITY_FIELDS:
        userdata.add_real(obj, field, DEFAULTS[field], g_obj, step=1.0)
    userdata.add_bool(obj, FIELD_USE_CAMERA_DIRECTION,
                      DEFAULTS[FIELD_USE_CAMERA_DIRECTION], g_obj)

    g_mat = userdata.add_group(obj, "Material Preview")
    userdata.add_bool(obj, FIELD_DOPPLER_PREVIEW, DEFAULTS[FIELD_DOPPLER_PREVIEW], g_mat)
    userdata.add_bool(obj, FIELD_SEARCHLIGHT_PREVIEW,
                      DEFAULTS[FIELD_SEARCHLIGHT_PREVIEW], g_mat)
    userdata.add_bool(obj, FIELD_LORENTZ_PREVIEW, DEFAULTS[FIELD_LORENTZ_PREVIEW], g_mat)

    g_int = userdata.add_group(obj, "Integration")
    userdata.add_bool(obj, FIELD_BAKE_ELIGIBLE, DEFAULTS[FIELD_BAKE_ELIGIBLE], g_int)
    userdata.add_bool(obj, FIELD_OCTANE_MATERIAL_SYNC,
                      DEFAULTS[FIELD_OCTANE_MATERIAL_SYNC], g_int)


# --- traversal ---------------------------------------------------------------
def _iter_objects(op):
    while op:
        yield op
        for child in _iter_objects(op.GetDown()):
            yield child
        op = op.GetNext()


# --- public utilities --------------------------------------------------------
def is_orc_object(obj):
    """``True`` if ``obj`` carries relativistic-object User Data.

    Matches on the object-specific field name, so it never reports ``True`` for
    the Relativity Controller or the camera (which use different field names).
    """
    return userdata.has_field(obj, FIELD_ORC_ENABLED)


def add_orc_object_data(obj):
    """Add object User Data to ``obj`` if missing. Returns ``True`` if it added any."""
    if obj is None or is_orc_object(obj):
        return False
    _build_user_data(obj)
    return True


def get_object_velocity(obj):
    """Return the object's velocity as a plain ``(x, y, z)`` tuple."""
    return (
        float(userdata.get_value(obj, FIELD_VELOCITY_X, 0.0) or 0.0),
        float(userdata.get_value(obj, FIELD_VELOCITY_Y, 0.0) or 0.0),
        float(userdata.get_value(obj, FIELD_VELOCITY_Z, 0.0) or 0.0),
    )


def read_orc_object_settings(obj):
    """Return all object fields as a ``{field_name: value}`` dict.

    Missing fields fall back to their default, so callers always get a complete
    dict. The three velocity components are present individually; use
    :func:`get_object_velocity` for an ``(x, y, z)`` tuple.
    """
    return {name: userdata.get_value(obj, name, DEFAULTS.get(name))
            for name in DEFAULTS}


def collect_orc_objects(doc):
    """Return a list of every relativistic object in ``doc`` (depth-first)."""
    if doc is None:
        return []
    return [op for op in _iter_objects(doc.GetFirstObject()) if is_orc_object(op)]
