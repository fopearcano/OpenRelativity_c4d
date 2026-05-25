"""Relativistic Camera Tag / tools - PLACEHOLDER (later phase).

Planned: a ``TagData`` attached to a Cinema 4D camera representing the observer's
frame - its velocity (combined with input via relativistic velocity addition,
see :func:`openrelativity_c4d.core.transforms.add_velocity`) and the camera
parameters (FOV, aspect) the math layer needs to turn screen directions into
world directions.

Intentionally a stub; ``import c4d`` is added when implemented. See
docs/ARCHITECTURE.md and docs/ROADMAP.md (Phase 1/2).
"""

from ..logging_utils import get_logger

log = get_logger("camera_tools")


def register():
    """Placeholder registration hook. Not implemented yet."""
    log.debug("Relativistic Camera Tag registration is not implemented yet.")
    return True
