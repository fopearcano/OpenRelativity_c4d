"""Object history samples for the (future) time-delay / light-cone system.

Pure Python, **no Cinema 4D imports**, standard library only. Everything is plain
numbers / tuples so the API stays portable and easy to port to C++ later (each
type maps onto a small struct / POD + ``std::vector`` / ``std::map``).

This module provides only the **data structures** the future light-travel-time
("retarded time") system will fill and query - it performs **no relativity
physics** yet. The existing constant-velocity solver in
:mod:`openrelativity_c4d.core.transforms` (``apparent_time_offset`` /
``apparent_position``) handles a single point moving at *constant* velocity; the
structures here generalise that to an **arbitrarily animated worldline** by
storing sampled transforms over scene time that a later solver can search and
interpolate. The full design is in ``docs/TIME_DELAY_LIGHT_CONE_DESIGN.md``.

Conventions:

* ``scene_time`` is the Cinema 4D document time in **seconds** (not frames), so
  the structures are frame-rate independent; the C4D layer converts frames <->
  seconds at the boundary (``c4d.BaseTime``).
* ``position`` / ``rotation`` / ``scale`` are plain ``(x, y, z)`` tuples.
  ``rotation`` is HPB Euler in **radians** (Cinema 4D's native order); ``scale``
  defaults to unit. The C4D layer converts to/from ``c4d.Matrix`` / ``c4d.Vector``.
"""

import bisect
from collections import namedtuple

#: Two scene times within this many seconds are treated as the same sample.
TIME_EPSILON = 1e-9


TransformSample = namedtuple(
    "TransformSample",
    ("scene_time", "position", "rotation", "scale"),
    defaults=((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
)
TransformSample.__doc__ = (
    "One sampled world transform of an object at a given scene time.\n\n"
    "Fields: ``scene_time`` (seconds), ``position`` (x, y, z), ``rotation`` "
    "(HPB radians, default identity), ``scale`` (default unit). Plain tuples so "
    "this is a POD-style record portable to C++."
)


def _lerp3(a, b, f):
    return (a[0] + (b[0] - a[0]) * f,
            a[1] + (b[1] - a[1]) * f,
            a[2] + (b[2] - a[2]) * f)


def lerp_sample(a, b, f):
    """Linearly interpolate samples ``a`` and ``b`` at fraction ``f`` in ``[0, 1]``.

    Position, scale, and rotation are interpolated component-wise and the result
    carries the interpolated ``scene_time``. NOTE: rotation is lerped on raw HPB
    angles - a deliberately simple placeholder; a proper quaternion slerp belongs
    in the physics phase, not in this data-structure helper.
    """
    t = a.scene_time + (b.scene_time - a.scene_time) * f
    return TransformSample(t,
                           _lerp3(a.position, b.position, f),
                           _lerp3(a.rotation, b.rotation, f),
                           _lerp3(a.scale, b.scale, f))


class ObjectHistory:
    """A time-ordered buffer of one object's sampled transforms.

    Identified by a stable ``key`` (the C4D layer passes the object's GUID /
    marker string). Samples are kept sorted by ``scene_time``; adding a sample at
    an existing time (within :data:`TIME_EPSILON`) replaces it. An optional
    ``max_samples`` bounds memory by dropping the oldest samples - a sliding
    window over the most recent scene times (see the frame-cache strategy in
    ``docs/TIME_DELAY_LIGHT_CONE_DESIGN.md``).
    """

    __slots__ = ("key", "name", "max_samples", "_samples")

    def __init__(self, key, name="", max_samples=None):
        self.key = key
        self.name = name
        self.max_samples = max_samples
        self._samples = []  # sorted by scene_time, ascending

    def __len__(self):
        return len(self._samples)

    def __iter__(self):
        return iter(self._samples)

    def __bool__(self):
        return bool(self._samples)

    def clear(self):
        self._samples = []

    def _times(self):
        return [s.scene_time for s in self._samples]

    def add(self, sample):
        """Insert or replace ``sample``, keeping the buffer time-sorted.

        A sample whose time matches an existing one (within :data:`TIME_EPSILON`)
        replaces it. When ``max_samples`` is set and exceeded, the oldest sample
        is dropped. Returns the stored sample. O(n) per insert (a prototype
        choice; fine for the bounded windows this is used with).
        """
        times = self._times()
        idx = bisect.bisect_left(times, sample.scene_time)
        if idx < len(times) and abs(times[idx] - sample.scene_time) <= TIME_EPSILON:
            self._samples[idx] = sample
        elif idx > 0 and abs(times[idx - 1] - sample.scene_time) <= TIME_EPSILON:
            self._samples[idx - 1] = sample
        else:
            self._samples.insert(idx, sample)
            if self.max_samples is not None and len(self._samples) > self.max_samples:
                self._samples.pop(0)
        return sample

    def extend(self, samples):
        """Add many samples (any order); each goes through :meth:`add`."""
        for sample in samples:
            self.add(sample)

    def earliest(self):
        """The oldest stored sample, or ``None`` when empty."""
        return self._samples[0] if self._samples else None

    def latest(self):
        """The most recent stored sample, or ``None`` when empty."""
        return self._samples[-1] if self._samples else None

    def time_span(self):
        """Return ``(min_time, max_time)`` in seconds, or ``None`` when empty."""
        if not self._samples:
            return None
        return (self._samples[0].scene_time, self._samples[-1].scene_time)

    def bracket(self, scene_time):
        """Return the two samples bracketing ``scene_time`` as ``(lo, hi)``.

        In range, ``lo.scene_time <= scene_time <= hi.scene_time``. Outside the
        range one side is ``None``: ``(None, first)`` before the start,
        ``(last, None)`` after the end. ``(None, None)`` when empty. On an exact
        time hit both entries are the same sample. The primitive used by
        :meth:`sample_at` / :meth:`nearest` and by a future retarded-time search.
        """
        if not self._samples:
            return (None, None)
        times = self._times()
        idx = bisect.bisect_left(times, scene_time)
        if idx < len(times) and abs(times[idx] - scene_time) <= TIME_EPSILON:
            sample = self._samples[idx]
            return (sample, sample)
        if idx == 0:
            return (None, self._samples[0])
        if idx == len(times):
            return (self._samples[-1], None)
        return (self._samples[idx - 1], self._samples[idx])

    def nearest(self, scene_time):
        """Return the stored sample whose time is closest to ``scene_time``."""
        lo, hi = self.bracket(scene_time)
        if lo is None:
            return hi
        if hi is None or lo is hi:
            return lo
        if abs(scene_time - lo.scene_time) <= abs(hi.scene_time - scene_time):
            return lo
        return hi

    def sample_at(self, scene_time):
        """Return the transform at ``scene_time``, linearly interpolated.

        Clamps to the endpoints outside the sampled range; returns ``None`` only
        when the history is empty. This is the primitive a future retarded-time
        solver calls once it has solved for the retarded scene time.
        """
        lo, hi = self.bracket(scene_time)
        if lo is None and hi is None:
            return None
        if lo is None:
            return hi
        if hi is None or lo is hi:
            return lo
        span = hi.scene_time - lo.scene_time
        if span <= TIME_EPSILON:
            return lo
        f = (scene_time - lo.scene_time) / span
        return lerp_sample(lo, hi, f)


class HistoryCache:
    """A keyed collection of :class:`ObjectHistory` (one per object).

    A thin container the C4D layer owns per document. ``version`` is a
    monotonically increasing token the host bumps via :meth:`invalidate` when the
    scene / animation / controller changes, so consumers can detect a stale cache
    and re-sample. This module does **not** decide *when* to invalidate - it only
    carries the token (see the frame-cache strategy in the design doc).
    """

    __slots__ = ("version", "_by_key")

    def __init__(self):
        self.version = 0
        self._by_key = {}

    def __len__(self):
        return len(self._by_key)

    def __contains__(self, key):
        return key in self._by_key

    def __iter__(self):
        return iter(self._by_key.values())

    def keys(self):
        return list(self._by_key.keys())

    def get(self, key):
        """Return the history for ``key``, or ``None``."""
        return self._by_key.get(key)

    def get_or_create(self, key, name="", max_samples=None):
        """Return the history for ``key``, creating an empty one if needed."""
        history = self._by_key.get(key)
        if history is None:
            history = ObjectHistory(key, name=name, max_samples=max_samples)
            self._by_key[key] = history
        return history

    def remove(self, key):
        """Drop one object's history; returns ``True`` if it existed."""
        return self._by_key.pop(key, None) is not None

    def clear(self):
        """Drop all histories (does not reset :attr:`version`)."""
        self._by_key = {}

    def invalidate(self):
        """Bump the version token; returns the new value."""
        self.version += 1
        return self.version
