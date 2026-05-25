"""Relativistic searchlight / beaming intensity (prototype approximation).

Renderer-agnostic, pure Python. **No Cinema 4D imports.**

The relativistic "searchlight" (beaming) effect brightens surfaces moving toward
the observer and dims those moving away. OpenRelativity scales intensity by
``(1 / shift)**3``; we reuse that here, blended by an art-directable ``strength``
and clamped so it can never return an absurd or non-finite value.

Convention matches :mod:`openrelativity_c4d.core.doppler`: ``cos_theta = +1`` is
approaching (brighter), ``cos_theta = -1`` is receding (dimmer).
"""

from .relativity_math import clamp
from .doppler import doppler_factor

#: Exponent applied to (1/factor); 3 matches OpenRelativity's shader.
BEAMING_EXPONENT = 3

#: Output multiplier is clamped to this range to stay finite and sane.
MIN_MULTIPLIER = 0.0
MAX_MULTIPLIER = 1000.0


def searchlight_intensity_multiplier(beta, cos_theta, strength=1.0):
    """Return an intensity multiplier for the beaming/searchlight effect.

    Prototype approximation. Computes the Doppler ``factor`` (so it shares the
    project's direction convention), raises ``(1/factor)`` to
    :data:`BEAMING_EXPONENT`, blends by ``strength`` (``0`` = no effect -> ``1.0``),
    and clamps to ``[MIN_MULTIPLIER, MAX_MULTIPLIER]``::

        raw  = (1 / doppler_factor(beta, cos_theta)) ** BEAMING_EXPONENT
        mult = clamp(1 + strength * (raw - 1), MIN_MULTIPLIER, MAX_MULTIPLIER)

    At rest (``beta == 0``) or ``strength == 0`` the multiplier is ``1.0``.
    Approaching gives ``> 1`` (brighter); receding gives ``< 1`` (dimmer).
    """
    factor = doppler_factor(beta, cos_theta)
    # doppler_factor is always positive, so this is safe.
    raw = (1.0 / factor) ** BEAMING_EXPONENT
    blended = 1.0 + strength * (raw - 1.0)
    return clamp(blended, MIN_MULTIPLIER, MAX_MULTIPLIER)
