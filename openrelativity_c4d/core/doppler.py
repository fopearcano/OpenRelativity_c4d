"""Relativistic Doppler shift.

Mirrors OpenRelativity's shader convention. The shift factor is the ratio of
observed to emitted wavelength::

    shift = (1 - beta * cos_theta) / sqrt(1 - beta**2)

where ``cos_theta`` is ``+1`` when the source moves directly **toward** the
observer (line-of-sight component of the relative velocity). Then:

* ``shift < 1`` -> wavelengths compressed -> **blueshift** (approaching),
* ``shift > 1`` -> wavelengths stretched  -> **redshift** (receding),
* ``cos_theta == 0`` -> ``shift = gamma > 1`` -> the transverse Doppler redshift.
"""

import math

_EPS = 1e-12


def doppler_shift(beta_rel, cos_theta):
    """Return the wavelength shift factor (observed / emitted).

    ``beta_rel`` is the relative speed over ``c`` (``0 <= beta_rel < 1``);
    ``cos_theta`` in ``[-1, 1]`` is ``+1`` toward the observer.
    """
    b2 = beta_rel * beta_rel
    if b2 >= 1.0 - _EPS:
        raise ValueError("beta_rel must satisfy 0 <= v/c < 1 (got {0!r})".format(beta_rel))
    return (1.0 - beta_rel * cos_theta) / math.sqrt(1.0 - b2)


def is_blueshift(shift):
    """``True`` if ``shift`` corresponds to a blueshift (approaching)."""
    return shift < 1.0


def is_redshift(shift):
    """``True`` if ``shift`` corresponds to a redshift (receding)."""
    return shift > 1.0
