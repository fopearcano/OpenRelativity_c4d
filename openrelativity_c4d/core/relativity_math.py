"""Core special-relativity scalar math.

Pure Python (``math`` only). Conventions:

* ``c`` is the speed of light in scene units. OpenRelativity keeps it adjustable
  (and small) so effects are visible at ordinary speeds; the default here is
  ``1.0`` so that velocities can be expressed directly as ``beta = v / c``.
* ``beta`` always means ``v / c`` and must satisfy ``|beta| < 1`` for finite
  results.
"""

import math

#: Default speed of light in scene units (adjustable by the Scene Controller).
DEFAULT_SPEED_OF_LIGHT = 1.0

#: Speeds within this of ``c`` are treated as "at c" to avoid division blow-ups.
_EPS = 1e-12


def beta(speed, c=DEFAULT_SPEED_OF_LIGHT):
    """Return ``v / c`` for a scalar ``speed``."""
    return speed / c


def gamma_from_beta(b):
    """Lorentz factor ``gamma = 1 / sqrt(1 - beta**2)``.

    Raises :class:`ValueError` if ``|b| >= 1`` (gamma diverges at ``c``).
    """
    b2 = b * b
    if b2 >= 1.0 - _EPS:
        raise ValueError("beta must satisfy |v/c| < 1 (got {0!r})".format(b))
    return 1.0 / math.sqrt(1.0 - b2)


def gamma(speed, c=DEFAULT_SPEED_OF_LIGHT):
    """Lorentz factor for a scalar ``speed`` (convenience wrapper)."""
    return gamma_from_beta(beta(speed, c))


def inverse_gamma_from_beta(b):
    """Return ``1 / gamma = sqrt(1 - beta**2)``.

    This is the factor OpenRelativity caches. Unlike :func:`gamma_from_beta`
    this is well defined at and beyond ``c`` (it clamps to ``0``), because the
    contracted/time-dilated quantities go smoothly to zero there.
    """
    b2 = b * b
    if b2 >= 1.0:
        return 0.0
    return math.sqrt(1.0 - b2)


def contract_length(rest_length, b):
    """Length contraction along the motion: ``L = L0 * sqrt(1 - beta**2)``."""
    return rest_length * inverse_gamma_from_beta(b)


def dilate_time(proper_time, b):
    """Observer (coordinate) time for a given proper time: ``dt = gamma * dtau``."""
    return proper_time * gamma_from_beta(b)


def add_velocities_collinear(u, v, c=DEFAULT_SPEED_OF_LIGHT):
    """Relativistic addition of two **collinear** velocities.

    ``w = (u + v) / (1 + u*v/c**2)``. Never exceeds ``c`` for ``|u|,|v| < c``,
    and adding ``c`` returns ``c``.
    """
    return (u + v) / (1.0 + (u * v) / (c * c))
