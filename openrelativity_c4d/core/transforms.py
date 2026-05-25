"""Vector helpers and relativistic geometric transforms.

Pure Python. Vectors are 3-tuples/lists of floats ``(x, y, z)``; functions
return tuples. No Cinema 4D vector types are used here so the module stays
testable and portable (the C4D layer converts to/from ``c4d.Vector``).
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


def normalize(a):
    """Return the unit vector along ``a`` (or ``(0,0,0)`` if ``a`` is zero)."""
    n = length(a)
    if n < _EPS:
        return (0.0, 0.0, 0.0)
    return (a[0] / n, a[1] / n, a[2] / n)


# --- relativistic velocity addition (3D) ------------------------------------
def add_velocity(v, u, c=DEFAULT_SPEED_OF_LIGHT):
    """Relativistically add velocity ``u`` (measured in the frame moving at
    ``v``) to frame velocity ``v``, returning the resulting lab-frame velocity.

    Uses the parallel/perpendicular decomposition (equivalent to
    OpenRelativity's rotate-to-axis approach)::

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

    inv_gamma = inverse_gamma_from_beta(v_mag / c)  # sqrt(1 - (v/c)^2)
    numerator = add(add(v, u_par), scale(u_perp, inv_gamma))
    denominator = 1.0 + dot(v, u) / (c * c)
    return scale(numerator, 1.0 / denominator)


# --- apparent position via light-travel-time (aberration / Terrell) ---------
def apparent_time_offset(rel_position, velocity, c=DEFAULT_SPEED_OF_LIGHT):
    """Solve for the (retarded) light-travel-time offset ``t``.

    Given a point currently at ``rel_position`` relative to the observer, moving
    at constant ``velocity``, find ``t`` such that light emitted at time ``t``
    (``t <= 0``, in the past) reaches the observer now. Solves::

        (c**2 - |v|**2) t**2 - 2 (r . v) t - |r|**2 = 0

    and returns the retarded root (OpenRelativity's ``tisw``). For a static point
    this is ``-|r| / c``.
    """
    a = c * c - dot(velocity, velocity)
    b = -2.0 * dot(rel_position, velocity)
    k = -dot(rel_position, rel_position)

    if abs(a) < _EPS:
        # Speed == c: linear equation b*t + k = 0.
        if abs(b) < _EPS:
            return 0.0
        return -k / b

    disc = b * b - 4.0 * a * k
    if disc < 0.0:
        disc = 0.0
    return (-b - math.sqrt(disc)) / (2.0 * a)


def apparent_position(rel_position, velocity, c=DEFAULT_SPEED_OF_LIGHT):
    """Return ``(apparent_rel_position, t)``.

    The apparent position is where the observer *sees* the moving point, i.e.
    its location at the retarded time: ``r + v * t``. ``t`` is the offset from
    :func:`apparent_time_offset`. For a static point the apparent position
    equals ``rel_position``.
    """
    t = apparent_time_offset(rel_position, velocity, c)
    return add(rel_position, scale(velocity, t)), t
