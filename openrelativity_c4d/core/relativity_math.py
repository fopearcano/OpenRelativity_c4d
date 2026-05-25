"""Core special-relativity scalar math (prototype approximations).

Renderer-agnostic, pure Python (``math`` only). **No Cinema 4D imports.**

These functions are intentionally *approximate, stable, and art-directable* - they
are not physics-grade. Stability is favoured over strict validity: instead of
raising when a velocity reaches or exceeds the speed of light, ``beta`` is clamped
to a safe maximum (:data:`MAX_BETA`) so downstream geometry/color never blows up.

Conventions used throughout the core:

* ``beta`` means ``v / c`` and is treated as a **magnitude** in ``[0, MAX_BETA]``;
  direction is carried separately (e.g. ``cos_theta`` in the Doppler functions).
* ``strength`` parameters in ``[0, 1]`` are art-directable blends: ``0`` disables
  the effect (identity), ``1`` applies the full approximate effect. Values above
  ``1`` are allowed for exaggeration but may need clamping by the caller.
"""

import math

#: Speeds at/above ``c`` are clamped to this fraction of ``c`` for stability.
MAX_BETA = 0.999

#: Default speed of light in scene units (the Scene Controller overrides this).
DEFAULT_SPEED_OF_LIGHT = 1.0


def clamp(value, lo, hi):
    """Clamp a scalar to ``[lo, hi]``."""
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def clamp01(value):
    """Clamp a scalar to ``[0.0, 1.0]``."""
    return clamp(value, 0.0, 1.0)


def clamp_beta(beta):
    """Clamp ``beta = v/c`` to the safe range ``[0.0, MAX_BETA]``.

    Negative inputs are clamped to ``0`` (``beta`` is a magnitude here) and any
    value at/above ``1`` is clamped to :data:`MAX_BETA` (default ``0.999``) so the
    Lorentz factor stays finite.
    """
    return clamp(beta, 0.0, MAX_BETA)


def beta_from_speed(speed, c_value):
    """Return the raw ratio ``beta = speed / c_value``.

    May be negative or exceed ``1``; callers that need a stable value should pass
    the result through :func:`clamp_beta`. A non-positive ``c_value`` is
    degenerate (everything is ultra-relativistic) and returns :data:`MAX_BETA`.
    """
    if c_value <= 0.0:
        return MAX_BETA
    return speed / c_value


def gamma_from_beta(beta):
    """Lorentz factor ``gamma = 1 / sqrt(1 - beta**2)`` (stable).

    ``beta`` is clamped via :func:`clamp_beta` first, so this never divides by
    zero or raises; ``gamma`` is ``1.0`` at ``beta == 0`` and increases
    monotonically with ``beta`` up to a finite maximum at :data:`MAX_BETA`.
    """
    b = clamp_beta(beta)
    return 1.0 / math.sqrt(1.0 - b * b)


def inverse_gamma_from_beta(beta):
    """Return ``1 / gamma = sqrt(1 - beta**2)`` (stable, clamped).

    This is the contraction / time-dilation factor. It is ``1.0`` at rest and
    approaches ``0`` as ``beta`` approaches :data:`MAX_BETA`.
    """
    b = clamp_beta(beta)
    return math.sqrt(1.0 - b * b)


def lorentz_contraction_scale(beta, strength=1.0):
    """Return the scale factor to apply **along the velocity axis**.

    Prototype approximation: the physical contraction is ``1/gamma``
    (:func:`inverse_gamma_from_beta`). ``strength`` blends between no contraction
    (``1.0``) and the full physical contraction::

        scale = 1 + strength * (inverse_gamma - 1)

    ``strength == 0`` returns ``1.0`` (geometry unchanged); ``strength == 1``
    returns the physical ``1/gamma``. The result decreases as ``beta`` increases
    (for ``strength > 0``) and stays in ``(0, 1]`` for ``strength`` in ``[0, 1]``.
    """
    inv_gamma = inverse_gamma_from_beta(beta)
    return 1.0 + strength * (inv_gamma - 1.0)
