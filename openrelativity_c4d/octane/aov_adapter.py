"""Octane AOV (render pass) integration - scaffolding only.

This defines the *desired* set of Relativity AOVs and a plan describing them,
plus best-effort render-settings detection. It does **not** create Octane AOVs:
there is no verified Octane AOV Python API/ID mapping yet, so automatic creation
is reported as **not supported** and the docs describe manual setup. Nothing here
raises or breaks if Octane (or Cinema 4D) is unavailable.

See docs/AOV_PIPELINE.md.

No top-level ``import c4d`` - import-safe everywhere.
"""

from collections import namedtuple

from ..logging_utils import get_logger
from . import detection

log = get_logger("octane.aov")

#: One desired AOV. ``kind`` is "scalar" / "vector" / "mask".
AOVSpec = namedtuple("AOVSpec", ["name", "kind", "description", "source", "compositing"])

#: The Relativity AOVs we want to expose for compositing (none auto-created yet).
RELATIVITY_AOVS = (
    AOVSpec(
        "ORC_DopplerFactor", "scalar",
        "Relativistic Doppler shift factor (observed/emitted wavelength); "
        "< 1 blueshift, > 1 redshift.",
        "core.doppler.doppler_factor per surface (approximate; per-object today).",
        "Drive a gradient/colour remap to retint or correct the beauty pass.",
    ),
    AOVSpec(
        "ORC_Beta", "scalar",
        "Effective speed as a fraction of c (v/c) of the surface.",
        "object_tools.effective_beta (Object Beta, or |velocity| / c).",
        "Mask/modulate effects by speed; isolate fast-moving regions.",
    ),
    AOVSpec(
        "ORC_Searchlight", "scalar",
        "Searchlight / beaming intensity multiplier.",
        "core.searchlight.searchlight_intensity_multiplier (approximate).",
        "Multiply or screen onto the beauty pass to brighten/dim by motion.",
    ),
    AOVSpec(
        "ORC_ObjectVelocity", "vector",
        "Object world-space velocity vector (scene units/second).",
        "Relativistic object User Data (Velocity X/Y/Z).",
        "Direction-aware grades; reconstruct motion vectors in the comp.",
    ),
    AOVSpec(
        "ORC_RelativityMask", "mask",
        "Coverage mask of which pixels belong to relativistic objects.",
        "Object/material ID of ORC objects (object buffer / ID mask).",
        "Constrain every relativity comp operation to the relativistic objects.",
    ),
)

#: What an automatic Octane AOV implementation still needs (documented, not assumed).
REQUIRED_OCTANE_AOV_INFO = [
    "Verified Octane render-settings / video-post container layout in the Python "
    "API (where AOVs/render passes live for the installed Octane version).",
    "The Octane Python API call(s) to add and name a custom AOV / render pass.",
    "Which Octane AOV types can carry custom scalar/vector data (render AOV "
    "nodes, material AOVs, object/material ID buffers).",
    "How to bind per-object data (Doppler / beta / searchlight) into a pass - "
    "likely via Octane material-AOV outputs or baked vertex/texture data.",
]

#: Manual setup summary (the full version is in docs/AOV_PIPELINE.md).
MANUAL_SETUP_STEPS = [
    "Render the beauty pass with Octane as usual.",
    "Add an Octane Object/Material ID (or render-layer) pass and assign the "
    "relativistic objects to it -> ORC_RelativityMask.",
    "For ORC_Beta / ORC_DopplerFactor / ORC_Searchlight, bake the per-object "
    "values (from the plugin's settings + core math) into a greyscale material "
    "or vertex colour and output it as a material AOV.",
    "For ORC_ObjectVelocity, encode the velocity vector as RGB in a material AOV.",
    "Composite in Fusion / Nuke / After Effects (see docs/AOV_PIPELINE.md).",
]


def get_relativity_aov_plan():
    """Return the desired Relativity AOV plan. Static, safe, no Cinema 4D needed.

    Keys: ``aovs`` (list[AOVSpec]), ``automatic_creation_supported`` (bool),
    ``reason`` (str), ``missing`` (list[str]), ``manual_setup`` (list[str]).
    """
    return {
        "aovs": list(RELATIVITY_AOVS),
        "automatic_creation_supported": False,
        "reason": ("Automatic Octane AOV creation is not implemented yet: the "
                   "Octane AOV Python API/IDs are not verified. Set the AOVs up "
                   "manually for now (see docs/AOV_PIPELINE.md)."),
        "missing": list(REQUIRED_OCTANE_AOV_INFO),
        "manual_setup": list(MANUAL_SETUP_STEPS),
    }


def aov_creation_supported(doc=None):
    """Return ``(supported, reason)``. Currently always unsupported (honest)."""
    if not detection.detect_octane_available():
        return False, "Octane not detected."
    return False, ("Octane detected, but automatic AOV creation is not implemented "
                   "yet (no verified Octane AOV API/IDs).")


def detect_render_settings(doc):
    """Best-effort render-settings detection (placeholder). Never raises.

    Returns ``{octane_detected, octane_renderer_active}`` from the safe detection
    layer - a starting point for future automatic AOV setup.
    """
    try:
        report = detection.get_octane_status_report(doc)
        return {
            "octane_detected": report.get("octane_detected", "unknown"),
            "octane_renderer_active": report.get("octane_renderer_active", "unknown"),
        }
    except Exception:  # noqa: BLE001
        return {"octane_detected": "unknown", "octane_renderer_active": "unknown"}


def create_relativity_aovs(doc):
    """Future entry point for automatic AOV creation. Safe no-op today.

    Returns a structured result and **never** modifies render settings or raises.
    """
    supported, reason = aov_creation_supported(doc)
    log.info("create_relativity_aovs: not creating AOVs (%s).", reason)
    return {
        "ok": False,
        "created": [],
        "reason": reason,
        "missing": list(REQUIRED_OCTANE_AOV_INFO),
    }


def format_aov_plan(plan, render_info=None):
    """Render the plan (+ optional render info) as a human-readable string."""
    def tri(value):
        if value is True:
            return "yes"
        if value is False:
            return "no"
        return "unknown"

    lines = []
    if render_info is not None:
        lines.append("Octane detected:        {0}".format(
            tri(render_info.get("octane_detected"))))
        lines.append("Octane renderer active: {0}".format(
            tri(render_info.get("octane_renderer_active"))))
        lines.append("")

    supported = plan.get("automatic_creation_supported")
    lines.append("Automatic Octane AOV creation: {0}".format(
        "supported" if supported else "NOT supported - manual setup required"))
    lines.append("")
    lines.append("Desired Relativity AOVs:")
    for spec in plan.get("aovs", []):
        lines.append("  - {0} [{1}]: {2}".format(spec.name, spec.kind, spec.description))
    lines.append("")
    lines.append(plan.get("reason", ""))
    lines.append("")
    lines.append("Manual setup (summary):")
    lines.extend("  - " + step for step in plan.get("manual_setup", []))
    lines.append("")
    lines.append("Full workflow & limitations: docs/AOV_PIPELINE.md")
    return "\n".join(lines)
