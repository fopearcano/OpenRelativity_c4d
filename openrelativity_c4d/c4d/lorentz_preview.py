"""Lorentz-like geometry preview via non-destructive scaled duplicates.

For each eligible relativistic object this creates a contracted **duplicate**
named ``ORC_LorentzPreview_<original name>`` and scales it along an approximate
velocity axis using :func:`openrelativity_c4d.core.relativity_math.lorentz_contraction_scale`.
The original object's **points are never edited**; the original is only
(optionally) hidden, and its visibility is restored when the preview is removed.

LIMITATIONS (first version - see docs/LORENTZ_PREVIEW.md):

* **Axis-aligned only.** The contraction is applied along the object's dominant
  **local** X/Y/Z axis (the largest component of the velocity), *not* an arbitrary
  world-space velocity direction. Diagonal motion or rotated objects are
  approximate.
* **No Terrell rotation / apparent geometry.** This is a simple length
  contraction look, not the true relativistic apparent shape.
* Works best on objects that are not nested inside other relativistic objects.

``import c4d`` here resolves to Cinema 4D's module (absolute import).
"""

import c4d

from ..core import relativity_math, transforms
from ..logging_utils import get_logger
from . import object_tools, scene_controller, userdata

log = get_logger("lorentz_preview")

#: Generated copies use this name prefix (single source of truth in object_tools).
PREFIX = object_tools.LORENTZ_PREVIEW_PREFIX

# User Data added to each copy, linking it back to its source for safe removal.
FIELD_SOURCE_LINK = "ORC Lorentz Source"
FIELD_SRC_EDITOR_VIS = "ORC Source Editor Visibility"
FIELD_SRC_RENDER_VIS = "ORC Source Render Visibility"


def _iter_objects(op):
    while op:
        yield op
        for child in _iter_objects(op.GetDown()):
            yield child
        op = op.GetNext()


def _settings(controller):
    get = scene_controller.get_value
    default_c = relativity_math.DEFAULT_SPEED_OF_LIGHT
    if controller is None:
        return {"enabled": True, "c": default_c, "global_beta": 0.0,
                "strength": 1.0, "hide": True}
    return {
        "enabled": bool(get(controller, scene_controller.FIELD_ENABLED, True)),
        "c": float(get(controller, scene_controller.FIELD_SPEED_OF_LIGHT, default_c) or default_c),
        "global_beta": float(get(controller, scene_controller.FIELD_BETA_OVERRIDE, 0.0) or 0.0),
        "strength": float(get(controller, scene_controller.FIELD_LORENTZ_STRENGTH, 1.0) or 1.0),
        "hide": bool(get(controller, scene_controller.FIELD_HIDE_ORIGINALS_LORENTZ, True)),
    }


def _collect_sources(doc):
    """Selected relativistic objects if any are selected, else all of them."""
    all_orc = object_tools.collect_orc_objects(doc)  # already excludes copies
    selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_0)
    selected_orc = [op for op in selected if object_tools.is_orc_object(op)]
    return selected_orc if selected_orc else all_orc


def _existing_copy(doc, source_name):
    target = PREFIX + source_name
    for op in _iter_objects(doc.GetFirstObject()):
        if op.GetName() == target:
            return op
    return None


def _make_copy(doc, source, settings):
    obj_settings = object_tools.read_orc_object_settings(source)
    if not obj_settings.get(object_tools.FIELD_ORC_ENABLED, True):
        return False
    if not obj_settings.get(object_tools.FIELD_LORENTZ_PREVIEW, True):
        return False

    # Idempotent re-run: drop any previous copy for this source first.
    previous = _existing_copy(doc, source.GetName())
    if previous is not None:
        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, previous)
        previous.Remove()

    velocity = object_tools.get_object_velocity(source)
    beta = object_tools.effective_beta(
        obj_settings, velocity, settings["c"], settings["global_beta"])
    contraction = relativity_math.lorentz_contraction_scale(beta, settings["strength"])

    axis = transforms.dominant_axis(velocity)
    if axis < 0:
        axis = 2  # no velocity direction: assume motion along local Z

    clone = source.GetClone(c4d.COPYFLAGS_0)
    if clone is None:
        return False
    clone.SetName(PREFIX + source.GetName())

    scale = clone.GetRelScale()
    components = [scale.x, scale.y, scale.z]
    components[axis] *= contraction
    clone.SetRelScale(c4d.Vector(components[0], components[1], components[2]))

    # The preview copy must be visible even if the source was hidden.
    clone.SetEditorMode(c4d.MODE_ON)
    clone.SetRenderMode(c4d.MODE_ON)

    # Link metadata + the source's original visibility (for safe restore).
    group = userdata.add_group(clone, "ORC Lorentz Preview")
    link_id = userdata.add_link(clone, FIELD_SOURCE_LINK, group)
    clone[link_id] = source
    userdata.add_long(clone, FIELD_SRC_EDITOR_VIS, source.GetEditorMode(), group)
    userdata.add_long(clone, FIELD_SRC_RENDER_VIS, source.GetRenderMode(), group)

    clone.InsertAfter(source)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, clone)

    if settings["hide"]:
        doc.AddUndo(c4d.UNDOTYPE_CHANGE, source)
        source.SetEditorMode(c4d.MODE_OFF)
        source.SetRenderMode(c4d.MODE_OFF)

    log.debug("Lorentz copy for %s: beta=%.3f scale=%.3f axis=%d",
              source.GetName(), beta, contraction, axis)
    return True


def create_preview(doc):
    """Create Lorentz preview copies. Returns ``(count, status)``.

    ``status`` is ``"ok"``, ``"disabled"`` (controller master Enabled off), or
    ``"no_objects"``.
    """
    if doc is None:
        return 0, "no_objects"
    settings = _settings(scene_controller.find_controller(doc))
    if not settings["enabled"]:
        return 0, "disabled"

    sources = _collect_sources(doc)
    if not sources:
        return 0, "no_objects"

    count = 0
    doc.StartUndo()
    for source in sources:
        try:
            if _make_copy(doc, source, settings):
                count += 1
        except Exception:  # noqa: BLE001 - keep going for the other objects
            log.exception("Failed to create Lorentz copy for %s.", source.GetName())
    doc.EndUndo()
    c4d.EventAdd()
    log.info("Created %d Lorentz preview copy(ies).", count)
    return count, "ok"


def remove_preview(doc):
    """Remove all Lorentz preview copies and restore originals' visibility.

    Returns the number of copies removed.
    """
    if doc is None:
        return 0
    copies = [op for op in _iter_objects(doc.GetFirstObject())
              if op.GetName().startswith(PREFIX)]
    if not copies:
        return 0

    removed = 0
    doc.StartUndo()
    for copy in copies:
        source = userdata.get_value(copy, FIELD_SOURCE_LINK, None)
        if source is not None:
            editor_vis = userdata.get_value(copy, FIELD_SRC_EDITOR_VIS, c4d.MODE_UNDEF)
            render_vis = userdata.get_value(copy, FIELD_SRC_RENDER_VIS, c4d.MODE_UNDEF)
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, source)
            source.SetEditorMode(int(editor_vis))
            source.SetRenderMode(int(render_vis))
        doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, copy)
        copy.Remove()
        removed += 1
    doc.EndUndo()
    c4d.EventAdd()
    log.info("Removed %d Lorentz preview copy(ies).", removed)
    return removed


def count_preview_copies(doc):
    """Return the number of Lorentz preview copies in the document."""
    if doc is None:
        return 0
    return sum(1 for op in _iter_objects(doc.GetFirstObject())
               if op.GetName().startswith(PREFIX))
