"""Detect an Octane-for-Cinema-4D integration without depending on it.

Every function is best-effort and never raises: if Octane (or Cinema 4D) is not
present, detection simply reports unavailable.
"""

from ..logging_utils import get_logger

log = get_logger("octane.detection")

#: Python module name(s) exposed by the Octane for Cinema 4D plugin. Kept as a
#: tuple so additional/alternate names can be added without touching callers.
OCTANE_MODULE_CANDIDATES = ("c4doctane",)


def octane_module():
    """Return the first importable Octane module, or ``None``."""
    for name in OCTANE_MODULE_CANDIDATES:
        try:
            return __import__(name)
        except Exception:  # noqa: BLE001 - any failure means "not available"
            continue
    return None


def is_octane_available():
    """Return ``True`` if an Octane integration module can be imported."""
    available = octane_module() is not None
    log.debug("Octane availability: %s", available)
    return available
