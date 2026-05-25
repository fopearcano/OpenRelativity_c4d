"""Relativity Scene Controller - PLACEHOLDER (later phase).

Planned: a scene-level element (``SceneHookData`` and/or a ``CommandData`` that
creates a controller object) owning the global relativistic state - the speed of
light ``c``, the observer's velocity, and the simulation time / time-dilation
mode - and distributing it to the camera and object tags.

This module is intentionally a stub. It does not import ``c4d`` yet because it
registers nothing; the ``import c4d`` line is added when the implementation
lands. See docs/ARCHITECTURE.md and docs/ROADMAP.md (Phase 1/2).
"""

from ..logging_utils import get_logger

log = get_logger("scene_controller")


def register():
    """Placeholder registration hook. Not implemented yet."""
    log.debug("Scene Controller registration is not implemented yet.")
    return True
