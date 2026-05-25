"""Relativity material preview (Standard/Physical) - Doppler + searchlight.

Generates one shared **Standard** material per object,
``ORC_Preview_<object name>``, and writes the approximate Doppler colour shift
and/or the searchlight (beaming) brightness/emission to it. Three commands drive
this with different effect combinations:

* Doppler only      -> ``apply_preview(doc, do_doppler=True,  do_searchlight=False)``
* Searchlight only  -> ``apply_preview(doc, do_doppler=False, do_searchlight=True)``
* Both (combined)   -> ``apply_preview(doc, do_doppler=True,  do_searchlight=True)``

Each call rewrites the material to a fully defined state, so the commands are
predictable and idempotent (running "Doppler only" resets brightness to neutral,
etc.). To see both effects at once use the combined command.

**Artistic approximation, not spectral/radiometric rendering** - see
docs/DOPPLER_PREVIEW.md and docs/SEARCHLIGHT_PREVIEW.md.

Non-destructive: existing materials are never modified. One extra Texture tag
links the generated material and overrides the object's look; *Clear* removes
only the ORC-generated tags and materials.

``import c4d`` here resolves to Cinema 4D's module (absolute import).
"""

import c4d

from ..core import doppler, relativity_math, searchlight, transforms
from ..logging_utils import get_logger
from . import camera_tools, object_tools, scene_controller

log = get_logger("preview_material")

#: Generated materials/tags are identified by this name prefix.
PREFIX = "ORC_Preview_"

#: Base colour used when an object has no readable material colour.
DEFAULT_BASE_COLOR = (0.8, 0.8, 0.8)

# --- artistic (NON-physical) clamps for the searchlight intensity -----------
#: Diffuse-brightness multiplier is clamped to this range (never fully black,
#: never absurdly bright) for a usable preview.
MIN_BRIGHTNESS = 0.05
MAX_BRIGHTNESS = 4.0
#: Above multiplier 1 we add a little luminance ("glow"); gain and cap here.
LUMINANCE_GAIN = 0.5
MAX_LUMINANCE = 1.0


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
            "searchlight_strength": 1.0,
        }
    get = scene_controller.get_value
    default_c = relativity_math.DEFAULT_SPEED_OF_LIGHT
    return {
        "enabled": bool(get(controller, scene_controller.FIELD_ENABLED, True)),
        "c": float(get(controller, scene_controller.FIELD_SPEED_OF_LIGHT, default_c) or default_c),
        "global_beta": float(get(controller, scene_controller.FIELD_BETA_OVERRIDE, 0.0) or 0.0),
        "doppler_strength": float(get(controller, scene_controller.FIELD_DOPPLER_STRENGTH, 1.0) or 1.0),
        "searchlight_strength": float(get(controller, scene_controller.FIELD_SEARCHLIGHT_STRENGTH, 1.0) or 1.0),
    }


# --- per-object math inputs --------------------------------------------------
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


def _compute_inputs(obj, obj_settings, settings, camera):
    """Return ``(beta, cos_theta)`` for an object."""
    velocity = object_tools.get_object_velocity(obj)
    beta = object_tools.effective_beta(
        obj_settings, velocity, settings["c"], settings["global_beta"])
    use_camera_direction = bool(
        obj_settings.get(object_tools.FIELD_USE_CAMERA_DIRECTION, True))
    los = _line_of_sight(obj, camera, use_camera_direction)
    return beta, transforms.cos_theta_towards_observer(velocity, los)


def _base_color(obj):
    """Best-effort read of the object's current colour from a non-ORC material."""
    base = DEFAULT_BASE_COLOR
    for tag in obj.GetTags():
        if tag.GetType() != c4d.Ttexture:
            continue
        mat = tag[c4d.TEXTURETAG_MATERIAL]
        if mat is None or mat.GetName().startswith(PREFIX):
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
            if mat is not None and mat.GetName().startswith(PREFIX):
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
def _object_color_and_multiplier(obj, obj_settings, settings, camera,
                                 do_doppler, do_searchlight):
    """Return ``(color, multiplier)`` for an object, or ``None`` if it is skipped.

    ``color`` is the (Doppler-shifted or base) ``(r, g, b)``; ``multiplier`` is the
    searchlight intensity multiplier (``1.0`` when searchlight is off).
    """
    if not obj_settings.get(object_tools.FIELD_ORC_ENABLED, True):
        return None

    eff_doppler = do_doppler and bool(
        obj_settings.get(object_tools.FIELD_DOPPLER_PREVIEW, True))
    eff_searchlight = do_searchlight and bool(
        obj_settings.get(object_tools.FIELD_SEARCHLIGHT_PREVIEW, True))
    if not (eff_doppler or eff_searchlight):
        return None

    beta, cos_theta = _compute_inputs(obj, obj_settings, settings, camera)
    base = _base_color(obj)

    if eff_doppler:
        factor = doppler.doppler_factor(beta, cos_theta)
        color = doppler.approximate_rgb_doppler_shift(
            base, factor, settings["doppler_strength"])
    else:
        color = base

    if eff_searchlight:
        multiplier = searchlight.searchlight_intensity_multiplier(
            beta, cos_theta, settings["searchlight_strength"])
    else:
        multiplier = 1.0
    return color, multiplier


def _write_material(doc, obj, color, multiplier):
    """Create/update the object's ``ORC_Preview_<name>`` Standard material.

    ``color`` is ``(r, g, b)``; ``multiplier`` is the searchlight intensity
    (``1.0`` = neutral). Returns the material.
    """
    brightness = relativity_math.clamp(multiplier, MIN_BRIGHTNESS, MAX_BRIGHTNESS)
    luminance_on = multiplier > 1.0
    luminance = (relativity_math.clamp(
        (multiplier - 1.0) * LUMINANCE_GAIN, 0.0, MAX_LUMINANCE)
        if luminance_on else 0.0)

    color_vec = c4d.Vector(color[0], color[1], color[2])
    mat = _get_or_create_material(doc, PREFIX + obj.GetName())
    mat[c4d.MATERIAL_USE_COLOR] = True
    mat[c4d.MATERIAL_COLOR_COLOR] = color_vec
    mat[c4d.MATERIAL_COLOR_BRIGHTNESS] = brightness
    mat[c4d.MATERIAL_USE_LUMINANCE] = luminance_on
    if luminance_on:
        mat[c4d.MATERIAL_LUMINANCE_COLOR] = color_vec
        mat[c4d.MATERIAL_LUMINANCE_BRIGHTNESS] = luminance
    mat.Update(True, True)

    _ensure_texture_tag(doc, obj, mat)
    return mat


def set_preview_material(doc, obj, color, intensity=1.0):
    """Public: write an object's preview material from an explicit colour and
    searchlight intensity. Used by the Octane adapter's Standard fallback so the
    result is identical to the native Standard preview (and Clear cleans it up).
    """
    return _write_material(doc, obj, color, 1.0 if intensity is None else intensity)


def _apply_to_object(doc, obj, settings, camera, do_doppler, do_searchlight,
                     writer=None):
    obj_settings = object_tools.read_orc_object_settings(obj)
    computed = _object_color_and_multiplier(
        obj, obj_settings, settings, camera, do_doppler, do_searchlight)
    if computed is None:
        return False
    color, multiplier = computed
    if writer is not None:
        writer(doc, obj, color, multiplier)
    else:
        _write_material(doc, obj, color, multiplier)
    log.debug("Preview %s: color=%s multiplier=%.3f", obj.GetName(), color, multiplier)
    return True


def apply_preview(doc, do_doppler=True, do_searchlight=True, writer=None):
    """Apply the relativity material preview to all eligible objects.

    ``do_doppler`` / ``do_searchlight`` select which effects to fold in (the
    per-object preview flags still gate each effect). ``writer`` is an optional
    ``callable(doc, obj, color, multiplier)`` that performs the actual material
    write; when ``None`` the built-in Standard material write is used. (The
    Octane-compatible command passes a writer that tries Octane first.) Returns
    ``(count, status)`` where ``status`` is ``"ok"``, ``"disabled"`` (controller
    master Enabled off), or ``"no_objects"``.
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
            if _apply_to_object(doc, obj, settings, camera, do_doppler,
                                do_searchlight, writer):
                count += 1
        except Exception:  # noqa: BLE001 - keep going for the other objects
            log.exception("Failed to apply preview to %s.", obj.GetName())
    doc.EndUndo()
    c4d.EventAdd()
    log.info("Applied material preview (doppler=%s, searchlight=%s) to %d object(s).",
             do_doppler, do_searchlight, count)
    return count, "ok"


def clear_preview(doc):
    """Remove all ORC preview tags and materials. Returns ``(tags, materials)``."""
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
            if mat is not None and mat.GetName().startswith(PREFIX):
                doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, tag)
                tag.Remove()
                removed_tags += 1

    # Then remove our materials.
    mat = doc.GetFirstMaterial()
    while mat:
        nxt = mat.GetNext()
        if mat.GetName().startswith(PREFIX):
            doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, mat)
            mat.Remove()
            removed_materials += 1
        mat = nxt
    doc.EndUndo()
    c4d.EventAdd()
    log.info("Cleared material preview: %d tag(s), %d material(s).",
             removed_tags, removed_materials)
    return removed_tags, removed_materials


def count_preview_materials(doc):
    """Return the number of ORC preview materials currently in the document."""
    if doc is None:
        return 0
    count = 0
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetName().startswith(PREFIX):
            count += 1
        mat = mat.GetNext()
    return count
