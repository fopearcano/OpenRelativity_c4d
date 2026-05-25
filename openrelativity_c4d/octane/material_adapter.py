"""Octane material adapter - PLACEHOLDER (Phase 3).

Will write the per-object Doppler color and searchlight intensity onto Octane
material nodes (e.g. diffuse/emission color and power). Stub for now.
"""

from ..logging_utils import get_logger

log = get_logger("octane.material")


def apply_doppler(material, base_color, intensity):
    """Apply Doppler/searchlight result to an Octane material. Not implemented yet."""
    log.debug("Octane material apply_doppler is a stub (Phase 1).")
    return False
