"""Octane adapter facade.

The rest of the plugin talks to Octane only through this small, stable API -
never to an Octane module directly. When Octane is unavailable, calls degrade
gracefully (safe no-ops or Standard-material fallbacks).

Implemented: detection/status (:func:`is_available`, :func:`status_report`) and
:func:`apply_octane_or_fallback_material` (tries Octane, falls back to the
Standard preview). The native Octane material/camera/AOV mapping is still future
work - see docs/OCTANE_INTEGRATION.md and docs/ROADMAP.md (Phase 3).
"""

from ..logging_utils import get_logger
from . import camera_adapter, detection, material_adapter

log = get_logger("octane.adapter")


def is_available():
    """Return ``True`` if an Octane integration was detected."""
    return detection.detect_octane_available()


def status_report(doc):
    """Return the safe Octane status dict (see ``detection.get_octane_status_report``)."""
    return detection.get_octane_status_report(doc)


def apply_octane_or_fallback_material(doc, obj, color, intensity):
    """Apply an Octane material to ``obj`` if feasible, else a Standard fallback.

    ``color`` is ``(r, g, b)``; ``intensity`` is the searchlight multiplier.
    Returns a structured result dict with keys ``ok``, ``method``
    (``"octane"`` / ``"fallback"`` / ``"error"``), ``warnings``, ``missing``.
    Never raises.

    Octane is tried first via
    :func:`material_adapter.create_or_update_octane_doppler_material`; if that is
    not feasible (no verified Octane mapping yet), it falls back to the Standard
    ``ORC_Preview`` material - which Octane can also render - so the preview always
    appears.
    """
    result = material_adapter.create_or_update_octane_doppler_material(
        doc, obj, color, intensity)
    if result.get("ok"):
        return result  # native Octane material applied (future)

    # Fall back to the Standard preview material (renderer-agnostic). Imported
    # lazily so this module stays import-safe without Cinema 4D.
    try:
        from ..c4d import preview_material

        preview_material.set_preview_material(doc, obj, color, intensity)
        result = dict(result)
        result["method"] = "fallback"
        result["ok"] = True
        result.setdefault("warnings", []).append(
            "Applied a Standard material fallback (ORC_Preview_<name>).")
        return result
    except Exception:  # noqa: BLE001
        log.exception("Standard material fallback failed.")
        result = dict(result)
        result["method"] = "error"
        result["ok"] = False
        result.setdefault("warnings", []).append("Standard fallback failed.")
        return result


def sync_camera(c4d_camera, observer_state):
    """Mirror observer/camera state onto an Octane camera. No-op stub in Phase 1."""
    if not is_available():
        return False
    return camera_adapter.sync(c4d_camera, observer_state)
