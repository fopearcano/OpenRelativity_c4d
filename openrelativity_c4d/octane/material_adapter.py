"""Octane material adapter (first stub/utility layer).

Goal: when Octane is available, create/update an Octane material carrying the
relativistic Doppler colour + searchlight intensity. When the exact Octane
material type/parameter IDs are unknown or unavailable, **fail gracefully** with a
structured warning so the caller can fall back to a Standard C4D material.

Current status: detection + structured reporting only. We do **not** yet have a
verified Octane material parameter mapping, so this never creates a
half-configured material - it reports ``unsupported`` and the caller falls back.
See :func:`required_octane_material_info` for exactly what is needed to finish
this, and docs/OCTANE_INTEGRATION.md.

No hard dependency on Octane: ``import c4d`` and any Octane access are guarded,
so importing this module is safe with neither installed.
"""

from ..logging_utils import get_logger
from . import detection

log = get_logger("octane.material")

#: Result ``method`` values returned by the functions here.
METHOD_OCTANE = "octane"          # an Octane material was created/updated
METHOD_UNAVAILABLE = "unavailable"  # Octane not detected
METHOD_UNSUPPORTED = "unsupported"  # Octane present but mapping not implemented


def _result(method, ok, warnings=None, missing=None):
    return {
        "ok": bool(ok),
        "method": method,
        "warnings": list(warnings or []),
        "missing": list(missing or []),
    }


def required_octane_material_info():
    """Document the exact Octane data still needed to implement this for real."""
    return [
        "Verified Octane material plugin/type ID (community-known candidate: "
        "{0}).".format(", ".join(str(i) for i in detection.OCTANE_MATERIAL_IDS)),
        "Which Octane material to target (e.g. diffuse vs. universal vs. "
        "standard-surface) and whether it is node-graph based on the installed "
        "Octane version.",
        "Description/parameter IDs (or node names) for the diffuse/albedo colour.",
        "Description/parameter IDs (or node names) for emission colour and power "
        "(to represent the searchlight intensity).",
        "How the chosen Octane version exposes these via the Python API "
        "(BaseMaterial parameters vs. GraphNode/NodeMaterial).",
    ]


def _octane_material_type_id():
    """Best-effort Octane material type ID, or ``None``. Never raises.

    Prefers an ID-independent name scan of registered material plugins; falls back
    to the known candidate IDs only if their plugins are actually registered.
    """
    try:
        import c4d
    except Exception:  # noqa: BLE001
        return None
    try:
        materials = c4d.plugins.FilterPluginList(c4d.PLUGINTYPE_MATERIAL, True) or []
        for plugin in materials:
            try:
                name = plugin.GetName() or ""
                if "octane" in name.lower():
                    return plugin.GetID()
            except Exception:  # noqa: BLE001
                continue
        for candidate in detection.OCTANE_MATERIAL_IDS:
            if c4d.plugins.FindPlugin(candidate, c4d.PLUGINTYPE_MATERIAL) is not None:
                return candidate
    except Exception:  # noqa: BLE001
        return None
    return None


def create_or_update_octane_doppler_material(doc, obj, color, intensity):
    """Try to create/update an Octane material for ``obj``.

    ``color`` is ``(r, g, b)``; ``intensity`` is the searchlight multiplier.
    Returns a structured result dict (see module docstring): ``ok`` is ``True``
    only if a native Octane material was actually configured. Never raises.

    In this first version it always reports ``unavailable`` (no Octane) or
    ``unsupported`` (Octane present, but no verified parameter mapping yet) so the
    caller falls back to a Standard material - it never creates a broken material.
    """
    if not detection.detect_octane_available():
        return _result(
            METHOD_UNAVAILABLE, False,
            warnings=["Octane not detected; cannot create an Octane material."])

    material_type = _octane_material_type_id()
    missing = required_octane_material_info()
    if material_type is None:
        return _result(
            METHOD_UNSUPPORTED, False,
            warnings=["Octane is present but its material type could not be "
                      "resolved; using the Standard fallback."],
            missing=missing)

    # We can resolve an Octane material type, but not its colour/emission
    # parameters reliably. Creating a material we cannot configure would be worse
    # than falling back, so we report and defer. (When the mapping in
    # required_octane_material_info() is known, build the material here and return
    # METHOD_OCTANE with ok=True.)
    log.info("Octane material type %s found, but parameter mapping is not "
             "implemented yet; falling back to Standard.", material_type)
    return _result(
        METHOD_UNSUPPORTED, False,
        warnings=["Octane material parameter IDs are not verified yet; cannot set "
                  "the Doppler colour/emission reliably. Using the Standard "
                  "fallback."],
        missing=missing)
