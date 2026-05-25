"""Relativistic searchlight / beaming (intensity) effect.

OpenRelativity scales the per-pixel tristimulus values by ``(1 / shift)**3``,
where ``shift`` is the Doppler factor from :mod:`openrelativity_c4d.core.doppler`.
Approaching (blueshifted, ``shift < 1``) surfaces brighten; receding
(redshifted, ``shift > 1``) surfaces dim.
"""

#: Exponent applied to (1/shift). 3 matches OpenRelativity's shader.
DEFAULT_BEAMING_EXPONENT = 3


def searchlight_intensity(shift, exponent=DEFAULT_BEAMING_EXPONENT):
    """Return the intensity scale factor for a given Doppler ``shift``.

    ``intensity = (1 / shift) ** exponent``. ``shift`` must be positive.
    """
    if shift <= 0.0:
        raise ValueError("shift must be positive (got {0!r})".format(shift))
    return (1.0 / shift) ** exponent
