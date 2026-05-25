"""Relativistic Doppler shift (prototype approximations).

Renderer-agnostic, pure Python. **No Cinema 4D imports.**

Convention (kept consistent across the whole core):

* ``cos_theta`` is the cosine of the angle between the line of sight and the
  relative motion, with **``cos_theta = +1`` meaning the source is approaching**
  the observer and ``cos_theta = -1`` meaning it is receding.
* The returned ``factor`` is the ratio of observed to emitted wavelength:
  ``factor < 1`` -> blueshift (approaching), ``factor > 1`` -> redshift
  (receding). ``factor == 1`` means no shift.

The color helper is deliberately *not* spectral; it is a simple, art-directable
red/blue tint so the prototype reads correctly without a spectral pipeline.
"""

import math

from .relativity_math import clamp, clamp01, clamp_beta


def doppler_factor(beta, cos_theta):
    """Approximate relativistic Doppler factor (observed / emitted wavelength).

    ``factor = (1 - beta * cos_theta) / sqrt(1 - beta**2)``

    ``beta`` is clamped to a safe range and ``cos_theta`` to ``[-1, 1]`` so the
    result is always finite and positive. With the project convention
    (``cos_theta = +1`` approaching), approaching gives ``factor < 1`` (blueshift)
    and receding gives ``factor > 1`` (redshift); a purely transverse view
    (``cos_theta = 0``) gives the transverse redshift ``factor = gamma > 1``.
    """
    b = clamp_beta(beta)
    ct = clamp(cos_theta, -1.0, 1.0)
    return (1.0 - b * ct) / math.sqrt(1.0 - b * b)


def is_blueshift(factor):
    """``True`` if ``factor`` is a blueshift (approaching, ``factor < 1``)."""
    return factor < 1.0


def is_redshift(factor):
    """``True`` if ``factor`` is a redshift (receding, ``factor > 1``)."""
    return factor > 1.0


def approximate_rgb_doppler_shift(base_rgb, factor, strength=1.0):
    """Tint an RGB color toward blue (approaching) or red (receding).

    Prototype approximation - **not** physically spectral. Drives a simple,
    art-directable shift from the Doppler ``factor``:

    * ``factor < 1`` (blueshift): push toward blue, pull down red.
    * ``factor > 1`` (redshift): push toward red, pull down blue.
    * ``factor == 1`` or ``strength == 0``: unchanged (input, clamped to 0..1).

    Args:
        base_rgb: ``(r, g, b)`` in ``0..1`` (out-of-range inputs are clamped).
        factor: Doppler factor from :func:`doppler_factor`.
        strength: art-directable amount in ``[0, 1]`` (``0`` = no shift).

    Returns:
        ``(r, g, b)`` tuple, each component clamped to ``[0.0, 1.0]``.
    """
    r = clamp01(base_rgb[0])
    g = clamp01(base_rgb[1])
    b = clamp01(base_rgb[2])

    # Signed shift: positive -> blue (approaching), negative -> red (receding).
    shift = clamp((1.0 - factor) * strength, -1.0, 1.0)

    if shift >= 0.0:  # blueshift / approaching
        amount = shift
        r = r * (1.0 - amount)
        g = g * (1.0 - 0.5 * amount)
        b = b + (1.0 - b) * amount
    else:  # redshift / receding
        amount = -shift
        r = r + (1.0 - r) * amount
        g = g * (1.0 - 0.5 * amount)
        b = b * (1.0 - amount)

    return (clamp01(r), clamp01(g), clamp01(b))
