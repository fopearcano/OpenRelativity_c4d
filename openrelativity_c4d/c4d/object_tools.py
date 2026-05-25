"""Relativistic Object Tag / tools - PLACEHOLDER (later phase).

Planned: a ``TagData`` attached to scene objects holding the object's world
velocity and the flags that drive its Lorentz deformation/bake, its approximate
Doppler/searchlight material adjustment, and its causal visibility window (an
object cannot be seen before its first light reaches the observer).

Intentionally a stub; ``import c4d`` is added when implemented. See
docs/ARCHITECTURE.md and docs/ROADMAP.md (Phase 1/2).
"""

from ..logging_utils import get_logger

log = get_logger("object_tools")


def register():
    """Placeholder registration hook. Not implemented yet."""
    log.debug("Relativistic Object Tag registration is not implemented yet.")
    return True
