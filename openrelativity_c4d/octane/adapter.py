"""Octane adapter facade.

The rest of the plugin talks to Octane only through this small, stable API -
never to an Octane module directly. When Octane is unavailable, calls are safe
no-ops that return ``False``/``None``.

Phase 1: stubs. The concrete mapping lives in the sibling ``*_adapter`` modules
and is implemented in Phase 3 (see docs/ROADMAP.md).
"""

from ..logging_utils import get_logger
from . import camera_adapter, detection, material_adapter

log = get_logger("octane.adapter")


def is_available():
    """Return ``True`` if an Octane integration was detected."""
    return detection.is_octane_available()


def apply_doppler_to_material(material, base_color, intensity):
    """Mirror a per-object Doppler/searchlight result onto an Octane material.

    ``material`` is a Cinema 4D material; ``base_color`` an ``(r, g, b)`` tuple;
    ``intensity`` the searchlight scale factor. Returns ``True`` on success.
    No-op stub in Phase 1.
    """
    if not is_available():
        return False
    return material_adapter.apply_doppler(material, base_color, intensity)


def sync_camera(c4d_camera, observer_state):
    """Mirror observer/camera state onto an Octane camera. No-op stub in Phase 1."""
    if not is_available():
        return False
    return camera_adapter.sync(c4d_camera, observer_state)
