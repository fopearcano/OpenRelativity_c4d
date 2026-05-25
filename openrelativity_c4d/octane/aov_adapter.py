"""Octane AOV adapter - PLACEHOLDER (Phase 3+).

Will optionally expose relativistic quantities (e.g. per-object Doppler shift or
beaming factor) as Octane render AOVs/passes for compositing. Stub for now.
"""

from ..logging_utils import get_logger

log = get_logger("octane.aov")


def register_aovs(render_data):
    """Register relativistic AOVs on an Octane render setup. Not implemented yet."""
    log.debug("Octane AOV registration is a stub (Phase 1).")
    return False
