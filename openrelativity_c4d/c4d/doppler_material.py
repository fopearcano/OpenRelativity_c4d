"""Approximate Doppler material preview (Standard/Physical materials).

The first *visible* effect. For each relativistic object whose *Doppler Material
Preview* is on, this computes an approximate relativistic Doppler colour shift
and applies it through a generated **Standard** material named
``ORC_Doppler_<object name>``.

This is an **artistic approximation, not spectral rendering** - see
docs/DOPPLER_PREVIEW.md. It works with the Standard/Physical renderers and never
requires Octane.

Non-destructive strategy
------------------------
We never remove an object's existing material tags. We add (or update) one extra
Texture tag that links our generated material; since later texture tags override
earlier ones for the whole object, this overrides the look without touching the
originals. *Clear* removes only our generated tags and materials, leaving the
originals intact.

``import c4d`` here resolves to Cinema 4D's module (absolute import).
"""

import c4d

from ..core import doppler, relativity_math, transforms
from ..logging_utils import get_logger
from . import camera_tools, object_tools, scene_controller

log = get_logger("doppler_material")

#: Generated materials/tags are identified by this name prefix.
MATERIAL_PREFIX = "ORC_Doppler_"

#: Base colour used when an object has no readable material colour.
DEFAULT_BASE_COLOR = (0.8, 0.8, 0.8)


# --- scene traversal ---------------------------------------------------------
def _iter_objects(op):
    while op:
        yield op
        for child in _iter_objects(op.GetDown()):
            yield child
        op = op.GetNext()


# --- controller settings -----------------------------------------------------
def _controller_settings(controller):
    """Read the controller fields we need, with safe defaults if absent."""
    if controller is None:
        return {
            "enabled": True,
            "c": relativity_math.DEFAULT_SPEED_OF_LIGHT,
            "global_beta": 0.0,
            "doppler_strength": 1.0,
        }
    get = scene_controller.get_value
    return {
        "enabled": bool(get(controller, scene_controller.FIELD_ENABLED, True)),
        "c": float(get(controller, scene_controller.FIELD_SPEED_OF_LIGHT,
                       relativity_math.DEFAULT_SPEED_OF_LIGHT)
                   or relativity_math.DEFAULT_SPEED_OF_LIGHT),
        "global_beta": float(get(controller, scene_controller.FIELD_BETA_OVERRIDE, 0.0) or 0.0),
        "doppler_strength": float(get(controller, scene_controller.FIELD_DOPPLER_STRENGTH, 1.0) or 1.0),
    }


# --- per-object math inputs --------------------------------------------------
def _object_beta(obj_settings, velocity, settings):
    """Effective beta: global override (if > 0), else object beta, else |v|/c."""
    if settings["global_beta"] > 0.0:
        return relativity_math.clamp_beta(settings["global_beta"])
    own = float(obj_settings.get(object_tools.FIELD_OBJECT_BETA, 0.0) or 0.0)
    if own > 0.0:
        return relativity_math.clamp_beta(own)
    speed = transforms.length(velocity)
    if speed > 0.0:
        return relativity_math.clamp_beta(
            relativity_math.beta_from_speed(speed, settings["c"]))
    return 0.0


def _line_of_sight(obj, camera, use_camera_direction):
    """Direction from the object **toward** the observer, as an (x, y, z) tuple."""
    obj_pos = obj.GetMg().off
    if camera is not None:
        mg = camera.GetMg()
        if use_camera_direction:
            d = mg.off - obj_pos  # true geometric line of sight
            return (d.x, d.y, d.z)
        fwd = mg.v3  # camera forward (+Z); toward camera is -forward
        return (-fwd.x, -fwd.y, -fwd.z)
    # No camera: assume the default viewer looks down +Z, so toward viewer is -Z.
    return (0.0, 0.0, -1.0)


def _base_color(obj):
    """Best-effort read of the object's current colour from a non-ORC material."""
    base = DEFAULT_BASE_COLOR
    for tag in obj.GetTags():
        if tag.GetType() != c4d.Ttexture:
            continue
        mat = tag[c4d.TEXTURETAG_MATERIAL]
        if mat is None or mat.GetName().startswith(MATERIAL_PREFIX):
            continue
        col = mat[c4d.MATERIAL_COLOR_COLOR]
        if col is not None:
            base = (col.x, col.y, col.z)
    return base


# --- material / tag plumbing -------------------------------------------------
def _find_material(doc, name):
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetName() == name:
            return mat
        mat = mat.GetNext()
    return None


def _get_or_create_material(doc, name):
    mat = _find_material(doc, name)
    if mat is not None:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, mat)
        return mat
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    mat.SetName(name)
    doc.InsertMaterial(mat)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, mat)
    return mat


def _orc_texture_tag(obj):
    for tag in obj.GetTags():
        if tag.GetType() == c4d.Ttexture:
            mat = tag[c4d.TEXTURETAG_MATERIAL]
            if mat is not None and mat.GetName().startswith(MATERIAL_PREFIX):
                return tag
    return None


def _ensure_texture_tag(doc, obj, mat):
    tag = _orc_texture_tag(obj)
    if tag is None:
        tag = c4d.BaseTag(c4d.Ttexture)
        obj.InsertTag(tag)
        doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, tag)
    else:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, tag)
    tag[c4d.TEXTURETAG_MATERIAL] = mat
    tag[c4d.TEXTURETAG_PROJECTION] = c4d.TEXTURETAG_PROJECTION_UVW
    return tag


# --- the effect --------------------------------------------------------------
def _apply_to_object(doc, obj, settings, camera):
    obj_settings = object_tools.read_orc_object_settings(obj)
    if not obj_settings.get(object_tools.FIELD_ORC_ENABLED, True):
        return False
    if not obj_settings.get(object_tools.FIELD_DOPPLER_PREVIEW, True):
        return False

    velocity = object_tools.get_object_velocity(obj)
    beta = _object_beta(obj_settings, velocity, settings)
    use_camera_direction = bool(
        obj_settings.get(object_tools.FIELD_USE_CAMERA_DIRECTION, True))
    los = _line_of_sight(obj, camera, use_camera_direction)
    cos_theta = transforms.cos_theta_towards_observer(velocity, los)

    factor = doppler.doppler_factor(beta, cos_theta)
    shifted = doppler.approximate_rgb_doppler_shift(
        _base_color(obj), factor, settings["doppler_strength"])

    mat = _get_or_create_material(doc, MATERIAL_PREFIX + obj.GetName())
    mat[c4d.MATERIAL_USE_COLOR] = True
    mat[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(shifted[0], shifted[1], shifted[2])
    mat.Message(c4d.MSG_UPDATE)
    mat.Update(True, True)

    _ensure_texture_tag(doc, obj, mat)
    log.debug("Doppler %s: beta=%.3f cosT=%.3f factor=%.3f -> %s",
              obj.GetName(), beta, cos_theta, factor, shifted)
    return True


def apply_preview(doc):
    """Apply the Doppler material preview to all eligible objects.

    Returns ``(count, status)`` where ``status`` is ``"ok"``, ``"disabled"`` (the
    controller's master Enabled is off), or ``"no_objects"``.
    """
    if doc is None:
        return 0, "no_objects"
    settings = _controller_settings(scene_controller.find_controller(doc))
    if not settings["enabled"]:
        return 0, "disabled"

    camera = camera_tools.find_relativistic_camera(doc)
    objects = object_tools.collect_orc_objects(doc)
    if not objects:
        return 0, "no_objects"

    count = 0
    doc.StartUndo()
    for obj in objects:
        try:
            if _apply_to_object(doc, obj, settings, camera):
                count += 1
        except Exception:  # noqa: BLE001 - keep going for the other objects
            log.exception("Failed to apply Doppler preview to %s.", obj.GetName())
    doc.EndUndo()
    c4d.EventAdd()
    log.info("Applied Doppler material preview to %d object(s).", count)
    return count, "ok"


def clear_preview(doc):
    """Remove all ORC Doppler tags and materials. Returns ``(tags, materials)``."""
    if doc is None:
        return 0, 0
    removed_tags = 0
    removed_materials = 0

    doc.StartUndo()
    # Remove our texture tags first (while their material link is still valid).
    for obj in _iter_objects(doc.GetFirstObject()):
        for tag in list(obj.GetTags()):
            if tag.GetType() != c4d.Ttexture:
                continue
            mat = tag[c4d.TEXTURETAG_MATERIAL]
            if mat is not None and mat.GetName().startswith(MATERIAL_PREFIX):
                doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, tag)
                tag.Remove()
                removed_tags += 1

    # Then remove our materials.
    mat = doc.GetFirstMaterial()
    while mat:
        nxt = mat.GetNext()
        if mat.GetName().startswith(MATERIAL_PREFIX):
            doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, mat)
            mat.Remove()
            removed_materials += 1
        mat = nxt
    doc.EndUndo()
    c4d.EventAdd()
    log.info("Cleared Doppler preview: %d tag(s), %d material(s).",
             removed_tags, removed_materials)
    return removed_tags, removed_materials


def count_preview_materials(doc):
    """Return the number of ORC Doppler materials currently in the document."""
    if doc is None:
        return 0
    count = 0
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetName().startswith(MATERIAL_PREFIX):
            count += 1
        mat = mat.GetNext()
    return count
