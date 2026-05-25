"""Vector helpers and relativistic geometric transforms (prototype).

Renderer-agnostic, pure Python. **No Cinema 4D imports** - vectors are plain
3-tuples/lists ``(x, y, z)`` and functions return tuples, so the C4D layer
converts to/from ``c4d.Vector`` at the boundary. These are approximate prototype
utilities, not physics-grade.
"""

import math

from .relativity_math import DEFAULT_SPEED_OF_LIGHT, inverse_gamma_from_beta

_EPS = 1e-12


# --- small vector algebra ---------------------------------------------------
def dot(a, b):
    """Dot product of two 3-vectors."""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def length(a):
    return math.sqrt(dot(a, a))


def safe_normalize(a, fallback=(0.0, 0.0, 0.0)):
    """Return the unit vector along ``a``; ``fallback`` if ``a`` is ~zero.

    Never divides by zero - the "safe" vector helper used wherever a direction
    might be degenerate (e.g. an object exactly at the observer).
    """
    n = length(a)
    if n < _EPS:
        return fallback
    return (a[0] / n, a[1] / n, a[2] / n)


#: Backwards-friendly alias; normalisation is always the safe variant here.
normalize = safe_normalize


# --- relativistic velocity addition (3D) ------------------------------------
def add_velocity(v, u, c=DEFAULT_SPEED_OF_LIGHT):
    """Relativistically add velocity ``u`` (in the frame moving at ``v``) to
    frame velocity ``v``, returning the lab-frame velocity.

    Parallel/perpendicular decomposition (prototype, stable)::

        w = (v + u_parallel + u_perp / gamma_v) / (1 + (v . u) / c**2)

    Reduces to ``u`` when ``v`` is zero and to the collinear formula when ``u``
    is parallel to ``v``.
    """
    v_mag = length(v)
    if v_mag < _EPS:
        return (float(u[0]), float(u[1]), float(u[2]))

    v_hat = (v[0] / v_mag, v[1] / v_mag, v[2] / v_mag)
    u_par_mag = dot(u, v_hat)
    u_par = scale(v_hat, u_par_mag)
    u_perp = sub(u, u_par)

    inv_gamma = inverse_gamma_from_beta(v_mag / c)  # sqrt(1 - (v/c)^2), clamped
    numerator = add(add(v, u_par), scale(u_perp, inv_gamma))
    denominator = 1.0 + dot(v, u) / (c * c)
    return scale(numerator, 1.0 / denominator)


# --- apparent position via light-travel-time (aberration / Terrell) ---------
def apparent_time_offset(rel_position, velocity, c=DEFAULT_SPEED_OF_LIGHT):
    """Solve for the (retarded) light-travel-time offset ``t`` (``t <= 0``).

    Finds when the light now reaching the observer left a point currently at
    ``rel_position`` moving at constant ``velocity``::

        (c**2 - |v|**2) t**2 - 2 (r . v) t - |r|**2 = 0

    Returns the retarded root (OpenRelativity's ``tisw``); for a static point this
    is ``-|r| / c``.
    """
    a = c * c - dot(velocity, velocity)
    b = -2.0 * dot(rel_position, velocity)
    k = -dot(rel_position, rel_position)

    if abs(a) < _EPS:
        # |v| == c: degenerate to a linear equation.
        if abs(b) < _EPS:
            return 0.0
        return -k / b

    disc = b * b - 4.0 * a * k
    if disc < 0.0:
        disc = 0.0
    return (-b - math.sqrt(disc)) / (2.0 * a)


def apparent_position(rel_position, velocity, c=DEFAULT_SPEED_OF_LIGHT):
    """Return ``(apparent_rel_position, t)`` - where the observer *sees* a moving
    point (its location at the retarded time ``r + v * t``). For a static point
    the apparent position equals ``rel_position``.
    """
    t = apparent_time_offset(rel_position, velocity, c)
    return add(rel_position, scale(velocity, t)), t


# --- direction toward the observer (the Doppler cos_theta) ------------------
def cos_theta_towards_observer(velocity, line_of_sight):
    """Cosine of the angle between the motion and the line of sight to the observer.

    ``line_of_sight`` points from the object **toward** the observer. Returns the
    ``cos_theta`` convention used by
    :func:`openrelativity_c4d.core.doppler.doppler_factor`:

    * ``+1`` - moving directly toward the observer (approaching),
    * ``-1`` - moving directly away (receding),
    * ``0``  - transverse, or undefined because either vector is ~zero.

    The result is clamped to ``[-1, 1]`` (guards against floating-point drift).
    """
    v = normalize(velocity)
    los = normalize(line_of_sight)
    if v == (0.0, 0.0, 0.0) or los == (0.0, 0.0, 0.0):
        return 0.0
    d = dot(v, los)
    if d < -1.0:
        return -1.0
    if d > 1.0:
        return 1.0
    return d
