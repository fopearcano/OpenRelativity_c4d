"""Octane material adapter.

When Octane is available, try to create/update a **native Octane material**
carrying the relativistic Doppler colour (and a rough searchlight emission), and
**fall back** to a Standard C4D material when that cannot be done reliably.

Reliability without hardcoded IDs: the Octane material *type* is discovered by a
plugin name scan, and its colour/emission parameters are found by **introspecting
the material's description at runtime** (matching parameter names like
"diffuse"/"albedo"/"colour"), then **verified by reading the value back**. The
attempt first runs on a throwaway material, so the scene is only touched once we
know setting works; otherwise we report ``unsupported`` and the caller falls back.

Safety: ``import c4d`` and all Octane access are guarded. With Octane absent this
returns ``unavailable`` immediately and never touches the scene.

NOTE: this native path is **untested outside Cinema 4D** and may not succeed on
node-graph-based Octane materials (where the diffuse lives in a node, not a
material parameter) - in that case it degrades to the Standard fallback. Use the
*Octane Diagnostics* command to see what was detected. See docs/OCTANE_INTEGRATION.md.
"""

from ..logging_utils import get_logger
from . import detection

log = get_logger("octane.material")

#: Result ``method`` values.
METHOD_OCTANE = "octane"            # a native Octane material was created/updated
METHOD_UNAVAILABLE = "unavailable"  # Octane not detected
METHOD_UNSUPPORTED = "unsupported"  # Octane present but native material not feasible

#: Parameter-name tokens (lowercased, substring match) used for description-based
#: discovery, in priority order.
DIFFUSE_TOKENS = ("diffuse", "albedo")
COLOR_TOKENS = ("color", "colour")
EMISSION_TOKENS = ("emission", "emit", "luminance")
POWER_TOKENS = ("power", "strength", "intensity")

_READBACK_TOL = 1e-3


def _result(method, ok, warnings=None, missing=None):
    return {
        "ok": bool(ok),
        "method": method,
        "warnings": list(warnings or []),
        "missing": list(missing or []),
    }


def required_octane_material_info():
    """Document the Octane data that would make this fully reliable."""
    return [
        "Confirmation of the Octane material type targeted (diffuse / universal / "
        "standard-surface) and whether it is node-graph based on the installed "
        "Octane version (node-based materials are not handled by description "
        "introspection and fall back to Standard).",
        "The diffuse/albedo colour parameter's description name or ID.",
        "The emission colour + power parameter names or IDs (for the searchlight).",
        "Run 'OpenRelativity C4D: Octane Diagnostics' inside Cinema 4D to capture "
        "the detected IDs/classes and material parameters.",
    ]


def octane_material_type_id():
    """Best-effort Octane material type ID, or ``None``. Never raises.

    ID-independent: prefers a name scan of registered material plugins, then the
    known candidate IDs only if their plugins are actually registered.
    """
    try:
        import c4d
    except Exception:  # noqa: BLE001
        return None
    try:
        materials = c4d.plugins.FilterPluginList(c4d.PLUGINTYPE_MATERIAL, True) or []
        for plugin in materials:
            try:
                if "octane" in (plugin.GetName() or "").lower():
                    return int(plugin.GetID())
            except Exception:  # noqa: BLE001
                continue
        for candidate in detection.OCTANE_MATERIAL_IDS:
            if c4d.plugins.FindPlugin(candidate, c4d.PLUGINTYPE_MATERIAL) is not None:
                return candidate
    except Exception:  # noqa: BLE001
        return None
    return None


def find_channel_descid(material, name_tokens, dtypes=None):
    """Return the DescID of the first description parameter whose name contains one
    of ``name_tokens`` (and whose dtype is in ``dtypes`` if given), else ``None``.

    Never raises. ID-independent (matches by parameter name at runtime).
    """
    try:
        import c4d  # noqa: F401
        description = material.GetDescription(c4d.DESCFLAGS_DESC_0)
    except Exception:  # noqa: BLE001
        return None
    if description is None:
        return None
    try:
        for bc, descid, _groupid in description:
            try:
                name = (bc[c4d.DESC_NAME] or "").lower()
                dtype = bc[c4d.DESC_DTYPE]
            except Exception:  # noqa: BLE001
                continue
            if dtypes is not None and dtype not in dtypes:
                continue
            if any(token in name for token in name_tokens):
                return descid
    except Exception:  # noqa: BLE001
        return None
    return None


def _color_dtypes(c4d):
    return tuple(d for d in (getattr(c4d, "DTYPE_COLOR", None),
                             getattr(c4d, "DTYPE_VECTOR", None)) if d is not None)


def _real_dtypes(c4d):
    return tuple(d for d in (getattr(c4d, "DTYPE_REAL", None),) if d is not None)


def _find_diffuse_descid(material, c4d):
    color_dtypes = _color_dtypes(c4d)
    for tokens in (DIFFUSE_TOKENS, COLOR_TOKENS):
        descid = find_channel_descid(material, tokens, color_dtypes)
        if descid is not None:
            return descid
    return None


def _vector_close(value, rgb):
    try:
        return (abs(value.x - rgb[0]) <= _READBACK_TOL
                and abs(value.y - rgb[1]) <= _READBACK_TOL
                and abs(value.z - rgb[2]) <= _READBACK_TOL)
    except Exception:  # noqa: BLE001
        return False


def _find_material_by_name(doc, name):
    mat = doc.GetFirstMaterial()
    while mat:
        if mat.GetName() == name:
            return mat
        mat = mat.GetNext()
    return None


def create_or_update_octane_doppler_material(doc, obj, color, intensity):
    """Create/update a native Octane material for ``obj`` if feasible.

    ``color`` is ``(r, g, b)``; ``intensity`` is the searchlight multiplier.
    Returns a structured result; ``ok``/``method == "octane"`` only when a native
    Octane material was actually created and verified. Never raises; never touches
    the scene unless native setting is confirmed working.
    """
    if not detection.detect_octane_available():
        return _result(METHOD_UNAVAILABLE, False,
                       warnings=["Octane not detected; cannot create an Octane material."])
    try:
        import c4d
    except Exception:  # noqa: BLE001
        return _result(METHOD_UNAVAILABLE, False, warnings=["Cinema 4D unavailable."])

    missing = required_octane_material_info()
    type_id = octane_material_type_id()
    if type_id is None:
        return _result(METHOD_UNSUPPORTED, False,
                       warnings=["Octane present but its material type could not be "
                                 "resolved; using the Standard fallback."],
                       missing=missing)

    color_vec = c4d.Vector(color[0], color[1], color[2])

    # 1) Feasibility probe on a throwaway material (no scene change).
    try:
        probe = c4d.BaseMaterial(type_id)
        if probe is None:
            raise RuntimeError("could not allocate Octane material")
        color_descid = _find_diffuse_descid(probe, c4d)
        if color_descid is None:
            return _result(METHOD_UNSUPPORTED, False,
                           warnings=["No nameable Octane diffuse/colour parameter "
                                     "found (node-based material?); using the "
                                     "Standard fallback. Try 'Octane Diagnostics'."],
                           missing=missing)
        probe[color_descid] = color_vec
        if not _vector_close(probe[color_descid], color):
            return _result(METHOD_UNSUPPORTED, False,
                           warnings=["Octane colour parameter did not accept a value "
                                     "(readback mismatch); using the Standard fallback."],
                           missing=missing)
        emission_descid = find_channel_descid(probe, EMISSION_TOKENS, _color_dtypes(c4d))
        power_descid = find_channel_descid(probe, POWER_TOKENS, _real_dtypes(c4d))
    except Exception:  # noqa: BLE001
        log.exception("Octane material probe failed; using the Standard fallback.")
        return _result(METHOD_UNSUPPORTED, False,
                       warnings=["Octane material probe failed; using the Standard fallback."],
                       missing=missing)

    # 2) Confirmed feasible -> apply for real (shares the ORC_Preview slot so
    #    'Clear Material Preview' removes it like any other preview material).
    try:
        from ..c4d import preview_material

        name = preview_material.PREFIX + obj.GetName()
        existing = _find_material_by_name(doc, name)
        if existing is not None and existing.GetType() != type_id:
            preview_material.remove_object_preview_tag(doc, obj)
            doc.AddUndo(c4d.UNDOTYPE_DELETEOBJ, existing)
            existing.Remove()
            existing = None
        if existing is not None:
            doc.AddUndo(c4d.UNDOTYPE_CHANGE, existing)
            mat = existing
        else:
            mat = c4d.BaseMaterial(type_id)
            mat.SetName(name)
            doc.InsertMaterial(mat)
            doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, mat)

        mat[color_descid] = color_vec
        if emission_descid is not None:
            mat[emission_descid] = color_vec
        if power_descid is not None:
            mat[power_descid] = float(max(0.0, intensity - 1.0))
        mat.Update(True, True)
        preview_material.ensure_preview_tag(doc, obj, mat)
    except Exception:  # noqa: BLE001
        log.exception("Failed to apply the Octane material; using the Standard fallback.")
        return _result(METHOD_UNSUPPORTED, False,
                       warnings=["Failed to apply the Octane material; using the Standard fallback."],
                       missing=missing)

    return _result(METHOD_OCTANE, True,
                   warnings=["Applied a native Octane material (experimental - "
                             "verify the look; node-based setups may differ)."])
