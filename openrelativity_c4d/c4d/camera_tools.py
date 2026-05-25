"""Relativistic Camera setup - a Camera object carrying organized User Data.

Like the Scene Controller, the observer is (for now) an ordinary Cinema 4D
**Camera** with structured **User Data** rather than a ``TagData`` plugin. The
"Setup Relativistic Camera" command uses the selected camera, or creates one
named ``ORC_Relativistic_Camera`` if none is selected.

This module owns the camera's User Data field names + defaults, creation/lookup,
and :func:`compute_observer_beta`, which resolves the observer's ``beta`` from the
camera's own data and (optionally) the Scene Controller. It reads the pure-Python
math core for clamping / beta-from-speed.

Octane and OSL fields are **stubs/placeholders** - this module never touches
Octane tags or generates OSL.

``import c4d`` here resolves to Cinema 4D's module (absolute import).
"""

import math

import c4d

from ..core import relativity_math
from ..logging_utils import get_logger
from . import scene_controller, userdata

log = get_logger("camera_tools")

#: Name used for a newly created relativistic camera.
CAMERA_NAME = "ORC_Relativistic_Camera"

# --- User Data field names (central identifiers for the camera) -------------
FIELD_ORC_ENABLED = "ORC Enabled"
FIELD_OBSERVER_BETA = "Observer Beta"
FIELD_VELOCITY = "Observer Velocity"
FIELD_USE_CONTROLLER_BETA = "Use Controller Global Beta"
FIELD_DOPPLER_PREVIEW = "Doppler Preview Enabled"
FIELD_SEARCHLIGHT_PREVIEW = "Searchlight Preview Enabled"
FIELD_ABERRATION_PREVIEW = "Aberration Preview Enabled"  # placeholder
FIELD_OCTANE_CAMERA_SYNC = "Octane Camera Sync Enabled"  # stub
FIELD_OSL_EXPERIMENTAL = "OSL Camera Experimental Enabled"  # placeholder

#: Safe defaults for the scalar/bool fields (velocity is handled separately).
DEFAULTS = {
    FIELD_ORC_ENABLED: True,
    FIELD_OBSERVER_BETA: 0.0,
    FIELD_USE_CONTROLLER_BETA: True,
    FIELD_DOPPLER_PREVIEW: True,
    FIELD_SEARCHLIGHT_PREVIEW: True,
    FIELD_ABERRATION_PREVIEW: False,
    FIELD_OCTANE_CAMERA_SYNC: False,
    FIELD_OSL_EXPERIMENTAL: False,
}


def _build_user_data(cam):
    """Attach the organized camera User Data with safe defaults."""
    g_cam = userdata.add_group(cam, "Relativistic Camera")
    userdata.add_bool(cam, FIELD_ORC_ENABLED, DEFAULTS[FIELD_ORC_ENABLED], g_cam)
    userdata.add_real(cam, FIELD_OBSERVER_BETA, DEFAULTS[FIELD_OBSERVER_BETA], g_cam,
                      min_val=0.0, max_val=0.999, step=0.001,
                      unit=c4d.DESC_UNIT_PERCENT)
    userdata.add_vector(cam, FIELD_VELOCITY, c4d.Vector(0.0, 0.0, 0.0), g_cam)
    userdata.add_bool(cam, FIELD_USE_CONTROLLER_BETA,
                      DEFAULTS[FIELD_USE_CONTROLLER_BETA], g_cam)

    g_prev = userdata.add_group(cam, "Preview")
    userdata.add_bool(cam, FIELD_DOPPLER_PREVIEW, DEFAULTS[FIELD_DOPPLER_PREVIEW], g_prev)
    userdata.add_bool(cam, FIELD_SEARCHLIGHT_PREVIEW,
                      DEFAULTS[FIELD_SEARCHLIGHT_PREVIEW], g_prev)
    userdata.add_bool(cam, FIELD_ABERRATION_PREVIEW,
                      DEFAULTS[FIELD_ABERRATION_PREVIEW], g_prev)

    g_int = userdata.add_group(cam, "Integration (Experimental)")
    userdata.add_bool(cam, FIELD_OCTANE_CAMERA_SYNC,
                      DEFAULTS[FIELD_OCTANE_CAMERA_SYNC], g_int)
    userdata.add_bool(cam, FIELD_OSL_EXPERIMENTAL,
                      DEFAULTS[FIELD_OSL_EXPERIMENTAL], g_int)


# --- detection / lookup ------------------------------------------------------
def get_selected_camera(doc):
    """Return the active object if it is a camera, else ``None``."""
    if doc is None:
        return None
    op = doc.GetActiveObject()
    if op is not None and op.GetType() == c4d.Ocamera:
        return op
    return None


def _iter_objects(op):
    while op:
        yield op
        for child in _iter_objects(op.GetDown()):
            yield child
        op = op.GetNext()


def find_relativistic_camera(doc):
    """Return the first camera carrying ORC User Data, or ``None``."""
    if doc is None:
        return None
    for op in _iter_objects(doc.GetFirstObject()):
        if op.GetType() == c4d.Ocamera and userdata.has_field(op, FIELD_ORC_ENABLED):
            return op
    return None


# --- creation / setup --------------------------------------------------------
def create_camera(doc):
    """Create a relativistic camera with User Data and insert it (undo-able)."""
    try:
        cam = c4d.BaseObject(c4d.Ocamera)
        if cam is None:
            log.error("Could not allocate a Camera object.")
            return None
        cam.SetName(CAMERA_NAME)
        _build_user_data(cam)
    except Exception:  # noqa: BLE001
        log.exception("Failed to build the relativistic camera.")
        return None

    doc.StartUndo()
    doc.InsertObject(cam)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, cam)
    doc.EndUndo()
    doc.SetActiveObject(cam)
    c4d.EventAdd()
    log.info("Created %s with default User Data.", CAMERA_NAME)
    return cam


def ensure_user_data(cam):
    """Add ORC User Data to ``cam`` if missing. Returns ``True`` if it added any."""
    if cam is None or userdata.has_field(cam, FIELD_ORC_ENABLED):
        return False
    _build_user_data(cam)
    return True


def setup_relativistic_camera(doc):
    """Use the selected camera or create one, ensuring its ORC User Data.

    Returns ``(camera, action)`` where ``action`` is one of
    ``"created"``, ``"configured"``, ``"exists"``, or ``"failed"``.
    """
    if doc is None:
        return None, "failed"

    cam = get_selected_camera(doc)
    if cam is None:
        created = create_camera(doc)
        return (created, "created") if created is not None else (None, "failed")

    # A camera is selected.
    if userdata.has_field(cam, FIELD_ORC_ENABLED):
        doc.SetActiveObject(cam)
        c4d.EventAdd()
        return cam, "exists"

    doc.StartUndo()
    doc.AddUndo(c4d.UNDOTYPE_CHANGE, cam)
    try:
        _build_user_data(cam)
    except Exception:  # noqa: BLE001
        log.exception("Failed to add camera User Data.")
        doc.EndUndo()
        return None, "failed"
    doc.EndUndo()
    doc.SetActiveObject(cam)
    c4d.EventAdd()
    return cam, "configured"


# --- read / write helpers ----------------------------------------------------
def get_value(camera, field_name, default=None):
    """Read a camera field by name; ``default`` if missing."""
    if camera is None:
        return default
    return userdata.get_value(camera, field_name, default)


def set_value(camera, field_name, value):
    """Write a camera field by name. Returns ``True`` on success."""
    if camera is None:
        return False
    return userdata.set_value(camera, field_name, value)


def get_observer_velocity(camera):
    """Return the observer velocity as a plain ``(x, y, z)`` tuple."""
    vel = userdata.get_value(camera, FIELD_VELOCITY, None)
    if vel is None:
        return (0.0, 0.0, 0.0)
    return (vel.x, vel.y, vel.z)


def read_state(camera):
    """Return all camera fields as a dict (velocity as an ``(x, y, z)`` tuple)."""
    state = {name: get_value(camera, name, DEFAULTS.get(name)) for name in DEFAULTS}
    state[FIELD_VELOCITY] = get_observer_velocity(camera)
    return state


# --- the actual relativity math hook ----------------------------------------
def compute_observer_beta(camera, controller=None):
    """Resolve the effective observer ``beta`` in ``[0, MAX_BETA]``.

    Priority (see docs/USER_GUIDE.md):

    1. If the camera's *Use Controller Global Beta* is on and ``controller`` has a
       *Global Beta Override* > 0, use that.
    2. Otherwise use the camera's own *Observer Beta* if > 0.
    3. Otherwise derive ``beta`` from ``|Observer Velocity| / c``, where ``c`` is
       the controller's *Artificial Speed of Light* (or the core default).

    Always clamped via :func:`openrelativity_c4d.core.relativity_math.clamp_beta`.
    """
    if camera is None:
        return 0.0

    use_global = bool(get_value(camera, FIELD_USE_CONTROLLER_BETA, False))
    if use_global and controller is not None:
        global_beta = scene_controller.get_value(
            controller, scene_controller.FIELD_BETA_OVERRIDE, 0.0) or 0.0
        if global_beta > 0.0:
            return relativity_math.clamp_beta(float(global_beta))

    own_beta = get_value(camera, FIELD_OBSERVER_BETA, 0.0) or 0.0
    if own_beta > 0.0:
        return relativity_math.clamp_beta(float(own_beta))

    vx, vy, vz = get_observer_velocity(camera)
    speed = math.sqrt(vx * vx + vy * vy + vz * vz)
    if speed > 0.0:
        c_value = relativity_math.DEFAULT_SPEED_OF_LIGHT
        if controller is not None:
            c_value = scene_controller.get_value(
                controller, scene_controller.FIELD_SPEED_OF_LIGHT, c_value) or c_value
        return relativity_math.clamp_beta(
            relativity_math.beta_from_speed(speed, c_value))

    return 0.0
