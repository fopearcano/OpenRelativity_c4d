"""Octane diagnostics - report detected Octane IDs / classes / parameters.

Read-only and safe: it queries the running Cinema 4D for Octane-looking plugins
(material / object / camera / tag / video-post) and, best-effort, introspects an
Octane material's description to list its colour/emission parameters. This is how
to capture the exact IDs/classes needed to finish native Octane support **inside
your own Cinema 4D + Octane environment** (none is available where this plugin is
built/tested). Never raises; reports "nothing" when Octane/Cinema 4D is absent.

No top-level ``import c4d`` - importable/testable anywhere.
"""

from ..logging_utils import get_logger
from . import detection, material_adapter

log = get_logger("octane.diagnostics")

#: Cap how many material parameters we list, to keep the report readable.
_MAX_PARAMS = 60


def _descid_str(descid):
    try:
        return "/".join(str(descid[i].id) for i in range(descid.GetDepth()))
    except Exception:  # noqa: BLE001
        return str(descid)


def _introspect_material_params(type_id):
    """Return ``[{name, descid, dtype}, ...]`` for a temp Octane material's
    colour/vector/real params. Never raises; the material is discarded."""
    params = []
    try:
        import c4d
    except Exception:  # noqa: BLE001
        return params
    try:
        material = c4d.BaseMaterial(type_id)
        if material is None:
            return params
        description = material.GetDescription(c4d.DESCFLAGS_DESC_0)
        if description is None:
            return params
        wanted = tuple(d for d in (getattr(c4d, "DTYPE_COLOR", None),
                                   getattr(c4d, "DTYPE_VECTOR", None),
                                   getattr(c4d, "DTYPE_REAL", None)) if d is not None)
        for bc, descid, _groupid in description:
            try:
                name = bc[c4d.DESC_NAME]
                dtype = bc[c4d.DESC_DTYPE]
            except Exception:  # noqa: BLE001
                continue
            if not name or (wanted and dtype not in wanted):
                continue
            params.append({"name": name, "descid": _descid_str(descid),
                           "dtype": int(dtype)})
            if len(params) >= _MAX_PARAMS:
                break
    except Exception:  # noqa: BLE001
        log.exception("Octane material introspection failed.")
    return params


def collect_diagnostics(doc=None):
    """Return a safe diagnostics dict. Never raises.

    Keys: ``octane_module_importable`` (bool), ``plugins`` (list of
    ``{name, id, type}``), ``material_type_id`` (int|None), ``material_parameters``
    (list of ``{name, descid, dtype}``), ``notes`` (list[str]).
    """
    data = {
        "octane_module_importable": False,
        "plugins": [],
        "material_type_id": None,
        "material_parameters": [],
        "notes": [],
    }
    try:
        data["octane_module_importable"] = detection.octane_module() is not None
    except Exception:  # noqa: BLE001
        pass
    try:
        data["plugins"] = detection.octane_plugins()
    except Exception:  # noqa: BLE001
        pass
    try:
        data["material_type_id"] = material_adapter.octane_material_type_id()
    except Exception:  # noqa: BLE001
        pass
    if data["material_type_id"] is not None:
        data["material_parameters"] = _introspect_material_params(data["material_type_id"])

    data["notes"] = [
        "Read-only: this command changes nothing in the scene or in Octane.",
        "Native Octane material support is discovered at runtime (no hardcoded "
        "IDs); share this report to help verify/extend it. See "
        "docs/OCTANE_INTEGRATION.md.",
    ]
    return data


def format_diagnostics(data):
    """Render a diagnostics dict as a human-readable multi-line string."""
    lines = [
        "Octane module importable: {0}".format(
            "yes" if data.get("octane_module_importable") else "no"),
        "Octane material type id:  {0}".format(
            data.get("material_type_id") if data.get("material_type_id") is not None
            else "not found"),
        "",
    ]
    plugins = data.get("plugins") or []
    if plugins:
        lines.append("Octane-looking plugins ({0}):".format(len(plugins)))
        for plug in plugins:
            lines.append("  - [{0}] id={1}  {2}".format(
                plug.get("type"), plug.get("id"), plug.get("name")))
    else:
        lines.append("Octane-looking plugins: none detected.")
    lines.append("")

    params = data.get("material_parameters") or []
    if params:
        lines.append("Octane material colour/real parameters ({0}):".format(len(params)))
        for p in params:
            lines.append("  - {0}  (descid {1}, dtype {2})".format(
                p.get("name"), p.get("descid"), p.get("dtype")))
    else:
        lines.append("Octane material parameters: none introspected.")
    lines.append("")
    lines.append("Notes:")
    lines.extend("- " + n for n in data.get("notes", []))
    return "\n".join(lines)
