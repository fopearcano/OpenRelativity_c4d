"""Detect an Octane-for-Cinema-4D integration without depending on it.

Every function here is **best-effort and never raises**: if Octane (or Cinema 4D
itself) is not present, detection simply reports unavailable/unknown. The core
plugin must keep working with Octane absent, so:

* there is **no top-level `import c4d`** and **no hard dependency on any Octane
  symbol**;
* the primary checks are a guarded module import (``c4doctane``) and a **name
  scan** of the registered Cinema 4D plugins - both independent of any specific
  Octane plugin ID, so unknown/changed IDs cannot break anything;
* known Octane plugin IDs are used only as optional *hints*.
"""

from ..logging_utils import get_logger

log = get_logger("octane.detection")

#: Python module name(s) exposed by the Octane for Cinema 4D plugin.
OCTANE_MODULE_CANDIDATES = ("c4doctane",)

#: Best-effort, community-known Octane-for-C4D plugin IDs. Used ONLY as optional
#: hints - detection never fails if these are wrong, missing, or change.
OCTANE_VIDEOPOST_IDS = (1029525,)  # Octane renderer (video post) - approximate
OCTANE_MATERIAL_IDS = (1029501,)   # Octane material - approximate

#: Substring used for the ID-independent plugin name scan.
_OCTANE_NAME_TOKEN = "octane"


def _c4d():
    """Return the Cinema 4D ``c4d`` module, or ``None`` if unavailable."""
    try:
        import c4d  # noqa: F401

        return c4d
    except Exception:  # noqa: BLE001
        return None


def octane_module():
    """Return the first importable Octane module, or ``None``."""
    for name in OCTANE_MODULE_CANDIDATES:
        try:
            return __import__(name)
        except Exception:  # noqa: BLE001 - any failure means "not available"
            continue
    return None


def _named_octane_plugins():
    """Return the names of registered plugins that look like Octane (back-compat)."""
    return [p["name"] for p in octane_plugins()]


#: Plugin categories scanned for Octane (label, c4d.PLUGINTYPE_* attribute name).
_PLUGIN_CATEGORIES = (
    ("material", "PLUGINTYPE_MATERIAL"),
    ("videopost", "PLUGINTYPE_VIDEOPOST"),
    ("shader", "PLUGINTYPE_SHADER"),
    ("object", "PLUGINTYPE_OBJECT"),
    ("tag", "PLUGINTYPE_TAG"),
)


def octane_plugins():
    """Return Octane-looking registered plugins as ``[{name, id, type}, ...]``.

    ID-independent (matches the name token "octane") and never raises; scans
    material / video-post / shader / object / tag categories so the diagnostic can
    surface material, camera (object/tag), and renderer IDs. Returns ``[]`` outside
    Cinema 4D.
    """
    c4d = _c4d()
    if c4d is None:
        return []
    found = []
    for label, attr in _PLUGIN_CATEGORIES:
        ptype = getattr(c4d, attr, None)
        if ptype is None:
            continue
        try:
            plugins = c4d.plugins.FilterPluginList(ptype, True) or []
        except Exception:  # noqa: BLE001
            continue
        for plugin in plugins:
            try:
                name = plugin.GetName()
                if name and _OCTANE_NAME_TOKEN in name.lower():
                    found.append({"name": name, "id": int(plugin.GetID()),
                                  "type": label})
            except Exception:  # noqa: BLE001
                continue
    return found


def detect_octane_available():
    """Return ``True`` if an Octane integration appears to be present.

    Combines a guarded module import with an ID-independent plugin name scan.
    Never raises; returns ``False`` when undeterminable or absent.
    """
    try:
        if octane_module() is not None:
            return True
        if _named_octane_plugins():
            return True
    except Exception:  # noqa: BLE001
        log.debug("Octane detection failed; treating as unavailable.", exc_info=True)
    return False


#: Backwards-compatible alias (older callers used this name).
is_octane_available = detect_octane_available


def _octane_renderer_active(c4d, doc):
    """Tri-state check of whether Octane is the document's active renderer.

    Returns ``True``/``False`` when determinable, else ``"unknown"``. Identifies
    Octane by the active engine's plugin **name** (ID-independent), with the known
    IDs as a fallback hint. Never raises.
    """
    try:
        render_data = doc.GetActiveRenderData()
        if render_data is None:
            return "unknown"
        engine_id = render_data[c4d.RDATA_RENDERENGINE]
        if engine_id == c4d.RDATA_RENDERENGINE_STANDARD:
            return False
        plugin = c4d.plugins.FindPlugin(engine_id, c4d.PLUGINTYPE_VIDEOPOST)
        if plugin is not None:
            return _OCTANE_NAME_TOKEN in (plugin.GetName() or "").lower()
        # Could not resolve the plugin by name; fall back to the ID hint.
        if engine_id in OCTANE_VIDEOPOST_IDS:
            return True
        return "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def get_octane_status_report(doc):
    """Return a safe Octane status dict. Never raises.

    Keys:
        ``octane_detected``        - ``True`` / ``False`` / ``"unknown"``
        ``octane_renderer_active`` - ``True`` / ``False`` / ``"unknown"``
        ``module_importable``      - ``bool``
        ``matched_plugins``        - ``list[str]`` (plugin names containing "octane")
        ``warnings``               - ``list[str]`` (limitations / guidance)
    """
    report = {
        "octane_detected": "unknown",
        "octane_renderer_active": "unknown",
        "module_importable": False,
        "matched_plugins": [],
        "warnings": [],
    }

    try:
        report["module_importable"] = octane_module() is not None
    except Exception:  # noqa: BLE001
        report["module_importable"] = False

    try:
        report["matched_plugins"] = _named_octane_plugins()
    except Exception:  # noqa: BLE001
        report["matched_plugins"] = []

    report["octane_detected"] = bool(
        report["module_importable"] or report["matched_plugins"])

    c4d = _c4d()
    if c4d is not None and doc is not None:
        report["octane_renderer_active"] = _octane_renderer_active(c4d, doc)
    else:
        report["octane_renderer_active"] = "unknown"

    report["warnings"] = _build_warnings(report)
    return report


def _build_warnings(report):
    warnings = [
        "Octane integration is NOT implemented yet - this is detection/status "
        "only. No Octane materials, cameras, render settings, or AOVs are touched.",
        "Full physical relativistic ray tracing inside Octane is NOT guaranteed; "
        "the relativistic look is approximated via materials/geometry.",
    ]
    detected = report.get("octane_detected")
    active = report.get("octane_renderer_active")
    if detected is True and active is False:
        warnings.append(
            "Octane appears installed but is not the active renderer. Previews "
            "use Standard/Physical materials today; the Octane adapter is future "
            "work.")
    elif detected is False:
        warnings.append(
            "Octane for Cinema 4D was not detected. The plugin runs fully without "
            "it - all previews work in Standard/Physical.")
    elif detected == "unknown":
        warnings.append(
            "Octane availability could not be determined; treating it as "
            "unavailable is safe.")
    return warnings


def format_status_report(report):
    """Render a status dict as a short human-readable multi-line string."""
    def tri(value):
        if value is True:
            return "yes"
        if value is False:
            return "no"
        return "unknown"

    lines = [
        "Octane detected:        {0}".format(tri(report.get("octane_detected"))),
        "Octane module import:   {0}".format(tri(report.get("module_importable"))),
        "Octane renderer active: {0}".format(tri(report.get("octane_renderer_active"))),
    ]
    matched = report.get("matched_plugins") or []
    if matched:
        lines.append("Matched plugins:        {0}".format(", ".join(matched)))
    lines.append("")
    lines.append("Notes:")
    lines.extend("- " + warning for warning in report.get("warnings", []))
    return "\n".join(lines)
