"""Relativity metadata export (JSON).

Collects the scene's relativistic state - controller settings, the active
relativistic camera, every relativistic object (settings, velocity, beta, and the
computed Doppler/searchlight factors), object names + GUID-like IDs, and the
frame/time - into a documented JSON file for renderer/post workflows, a future
RelativityRender bridge, debugging, and reproducibility.

No external dependencies (standard-library :mod:`json`). Import-safe: there is no
top-level ``import c4d``; Cinema-4D access happens lazily inside
:func:`collect_metadata`, so :func:`to_json`, :func:`default_filename`, and the
schema constants can be used/tested without Cinema 4D. See docs/METADATA_SCHEMA.md.
"""

import json

from ..logging_utils import get_logger

log = get_logger("export.metadata")

#: Schema identity (bump SCHEMA_VERSION on breaking changes).
SCHEMA_NAME = "openrelativity_c4d.metadata"
SCHEMA_VERSION = 1

#: Standing caveats included in every export.
APPROXIMATION_NOTES = [
    "Doppler/searchlight factors and beta are artistic approximations, not "
    "spectral/radiometric values.",
    "beta is object/global; the camera's own velocity is not yet combined into a "
    "true relative beta.",
    "cos_theta uses the object pivot vs. the camera viewing axis / line of sight "
    "(per-object, not per-pixel).",
    "Settings dictionaries mirror the User Data field names verbatim.",
]


# --- small, c4d-free helpers (operate on values passed in) ------------------
def _sanitize(value):
    """Make a value JSON-serializable (tuples->lists; unknowns->str)."""
    if isinstance(value, dict):
        return {str(key): _sanitize(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)  # last resort for any stray non-JSON type


def _safe_guid(obj):
    try:
        return int(obj.GetGUID())
    except Exception:  # noqa: BLE001
        return None


def _vec3(vector):
    try:
        return [float(vector.x), float(vector.y), float(vector.z)]
    except Exception:  # noqa: BLE001
        return None


def _world_position(obj):
    try:
        return _vec3(obj.GetMg().off)
    except Exception:  # noqa: BLE001
        return None


def _document_info(doc):
    info = {"name": None, "path": None, "fps": None, "frame": None,
            "time_seconds": None}
    if doc is None:
        return info
    try:
        info["name"] = doc.GetDocumentName()
    except Exception:  # noqa: BLE001
        pass
    try:
        info["path"] = doc.GetDocumentPath()
    except Exception:  # noqa: BLE001
        pass
    try:
        fps = doc.GetFps()
        time = doc.GetTime()
        info["fps"] = int(fps)
        info["frame"] = int(time.GetFrame(fps))
        info["time_seconds"] = float(time.Get())
    except Exception:  # noqa: BLE001
        pass
    return info


# --- collection --------------------------------------------------------------
def collect_metadata(doc):
    """Collect the relativity metadata for ``doc`` into a JSON-ready dict.

    Safe with ``doc=None`` (returns the schema skeleton without importing c4d).
    """
    from .. import constants

    metadata = {
        "schema": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "plugin": constants.PLUGIN_NAME,
        "plugin_version": constants.PLUGIN_VERSION,
        "document": _document_info(doc),
        "controller": {"present": False},
        "camera": {"present": False},
        "objects": [],
        "approximation_notes": list(APPROXIMATION_NOTES),
    }
    if doc is None:
        return metadata

    import c4d  # noqa: F401  (presence/parity; lazy so the module stays import-safe)
    from ..c4d import (
        camera_tools,
        object_tools,
        preview_material,
        scene_controller,
    )

    controller = scene_controller.find_controller(doc)
    camera = camera_tools.find_relativistic_camera(doc)

    metadata["controller"] = _controller_info(controller, scene_controller)
    metadata["camera"] = _camera_info(camera, controller, camera_tools)
    metadata["objects"] = [
        _object_info(obj, controller, camera, object_tools, preview_material)
        for obj in object_tools.collect_orc_objects(doc)
    ]
    return metadata


def _controller_info(controller, scene_controller):
    if controller is None:
        return {"present": False}
    return {
        "present": True,
        "name": controller.GetName(),
        "guid": _safe_guid(controller),
        "position": _world_position(controller),
        "settings": _sanitize(scene_controller.read_state(controller)),
    }


def _camera_info(camera, controller, camera_tools):
    if camera is None:
        return {"present": False}
    info = {
        "present": True,
        "name": camera.GetName(),
        "guid": _safe_guid(camera),
        "position": _world_position(camera),
        "settings": _sanitize(camera_tools.read_state(camera)),
        "observer_beta": None,
    }
    try:
        info["observer_beta"] = float(
            camera_tools.compute_observer_beta(camera, controller))
    except Exception:  # noqa: BLE001
        pass
    return info


def _object_info(obj, controller, camera, object_tools, preview_material):
    velocity = object_tools.get_object_velocity(obj)
    info = {
        "name": obj.GetName(),
        "guid": _safe_guid(obj),
        "position": _world_position(obj),
        "velocity": [float(velocity[0]), float(velocity[1]), float(velocity[2])],
        "settings": _sanitize(object_tools.read_orc_object_settings(obj)),
        "beta": None,
        "cos_theta": None,
        "doppler_factor": None,
        "searchlight_multiplier": None,
    }
    try:
        factors = preview_material.compute_object_factors(controller, camera, obj)
        info["beta"] = float(factors["beta"])
        info["cos_theta"] = float(factors["cos_theta"])
        info["doppler_factor"] = float(factors["doppler_factor"])
        info["searchlight_multiplier"] = float(factors["searchlight_multiplier"])
    except Exception:  # noqa: BLE001
        log.exception("Failed to compute factors for %s.", info["name"])
    return info


# --- serialization / export --------------------------------------------------
def to_json(metadata, indent=2):
    """Serialize a metadata dict to a JSON string (stdlib only)."""
    return json.dumps(metadata, indent=indent, sort_keys=False)


def default_filename(doc):
    """Suggest a JSON filename, including the current frame when available."""
    suffix = ""
    try:
        if doc is not None:
            fps = doc.GetFps()
            suffix = "_f{0}".format(int(doc.GetTime().GetFrame(fps)))
    except Exception:  # noqa: BLE001
        suffix = ""
    return "ORC_metadata{0}.json".format(suffix)


def export_metadata_json(doc, path):
    """Collect and write the metadata JSON to ``path``. Never raises hard.

    Returns ``{ok, path, error, object_count}``.
    """
    try:
        metadata = collect_metadata(doc)
        with open(path, "w") as handle:
            handle.write(to_json(metadata))
        count = len(metadata.get("objects", []))
        log.info("Exported relativity metadata (%d objects) to %s", count, path)
        return {"ok": True, "path": path, "error": None, "object_count": count}
    except Exception as exc:  # noqa: BLE001
        log.exception("Failed to export metadata to %s", path)
        return {"ok": False, "path": path, "error": str(exc), "object_count": 0}
