"""Unit tests for the object-history data structures (pure Python, no `c4d`).

These cover the storage/query behaviour the future time-delay / light-cone system
relies on (see docs/TIME_DELAY_LIGHT_CONE_DESIGN.md). No relativity physics is
exercised here - none is implemented yet.
"""

import unittest

from openrelativity_c4d.core import history
from openrelativity_c4d.core.history import (HistoryCache, ObjectHistory,
                                             TransformSample, lerp_sample)


def _sample(t, x):
    """A sample at time ``t`` with position (x, 0, 0)."""
    return TransformSample(t, (x, 0.0, 0.0))


class TestModuleIsPure(unittest.TestCase):
    def test_no_c4d_dependency(self):
        self.assertFalse(hasattr(history, "c4d"))


class TestTransformSample(unittest.TestCase):
    def test_defaults(self):
        s = TransformSample(1.0, (1.0, 2.0, 3.0))
        self.assertEqual(s.scene_time, 1.0)
        self.assertEqual(s.position, (1.0, 2.0, 3.0))
        self.assertEqual(s.rotation, (0.0, 0.0, 0.0))
        self.assertEqual(s.scale, (1.0, 1.0, 1.0))

    def test_lerp_midpoint(self):
        a = TransformSample(0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
        b = TransformSample(2.0, (10.0, 0.0, 0.0), (2.0, 2.0, 2.0), (3.0, 3.0, 3.0))
        mid = lerp_sample(a, b, 0.5)
        self.assertAlmostEqual(mid.scene_time, 1.0)
        self.assertAlmostEqual(mid.position[0], 5.0)
        self.assertAlmostEqual(mid.rotation[0], 1.0)
        self.assertAlmostEqual(mid.scale[0], 2.0)


class TestObjectHistoryAdd(unittest.TestCase):
    def test_kept_time_sorted_regardless_of_insert_order(self):
        h = ObjectHistory("k")
        h.extend([_sample(2.0, 2.0), _sample(0.0, 0.0), _sample(1.0, 1.0)])
        self.assertEqual([s.scene_time for s in h], [0.0, 1.0, 2.0])
        self.assertEqual(len(h), 3)
        self.assertTrue(h)

    def test_empty_is_falsey(self):
        self.assertFalse(ObjectHistory("k"))

    def test_same_time_replaces(self):
        h = ObjectHistory("k")
        h.add(_sample(1.0, 1.0))
        h.add(_sample(1.0, 9.0))  # same time -> replace, not duplicate
        self.assertEqual(len(h), 1)
        self.assertEqual(h.latest().position[0], 9.0)

    def test_max_samples_drops_oldest(self):
        h = ObjectHistory("k", max_samples=3)
        for t in range(5):
            h.add(_sample(float(t), float(t)))
        self.assertEqual(len(h), 3)
        self.assertEqual([s.scene_time for s in h], [2.0, 3.0, 4.0])

    def test_clear(self):
        h = ObjectHistory("k")
        h.add(_sample(0.0, 0.0))
        h.clear()
        self.assertEqual(len(h), 0)


class TestObjectHistoryQuery(unittest.TestCase):
    def setUp(self):
        self.h = ObjectHistory("k")
        self.h.extend([_sample(0.0, 0.0), _sample(1.0, 10.0), _sample(2.0, 20.0)])

    def test_time_span(self):
        self.assertEqual(self.h.time_span(), (0.0, 2.0))
        self.assertIsNone(ObjectHistory("k").time_span())

    def test_earliest_latest(self):
        self.assertEqual(self.h.earliest().scene_time, 0.0)
        self.assertEqual(self.h.latest().scene_time, 2.0)
        self.assertIsNone(ObjectHistory("k").earliest())

    def test_bracket_between(self):
        lo, hi = self.h.bracket(0.5)
        self.assertEqual((lo.scene_time, hi.scene_time), (0.0, 1.0))

    def test_bracket_exact_hit_returns_same_sample(self):
        lo, hi = self.h.bracket(1.0)
        self.assertIs(lo, hi)
        self.assertEqual(lo.scene_time, 1.0)

    def test_bracket_out_of_range(self):
        self.assertEqual(self.h.bracket(-1.0), (None, self.h.earliest()))
        self.assertEqual(self.h.bracket(99.0), (self.h.latest(), None))
        self.assertEqual(ObjectHistory("k").bracket(0.0), (None, None))

    def test_nearest(self):
        self.assertEqual(self.h.nearest(0.4).scene_time, 0.0)
        self.assertEqual(self.h.nearest(0.6).scene_time, 1.0)
        self.assertEqual(self.h.nearest(-5.0).scene_time, 0.0)
        self.assertEqual(self.h.nearest(5.0).scene_time, 2.0)

    def test_sample_at_interpolates(self):
        s = self.h.sample_at(0.5)
        self.assertAlmostEqual(s.scene_time, 0.5)
        self.assertAlmostEqual(s.position[0], 5.0)

    def test_sample_at_clamps_to_endpoints(self):
        self.assertAlmostEqual(self.h.sample_at(-3.0).position[0], 0.0)
        self.assertAlmostEqual(self.h.sample_at(7.0).position[0], 20.0)

    def test_sample_at_exact_hit(self):
        self.assertAlmostEqual(self.h.sample_at(1.0).position[0], 10.0)

    def test_sample_at_empty_is_none(self):
        self.assertIsNone(ObjectHistory("k").sample_at(0.0))


class TestHistoryCache(unittest.TestCase):
    def test_get_or_create_is_idempotent(self):
        cache = HistoryCache()
        a = cache.get_or_create("obj-1", name="Cube")
        b = cache.get_or_create("obj-1")
        self.assertIs(a, b)
        self.assertEqual(len(cache), 1)
        self.assertEqual(a.name, "Cube")

    def test_get_and_contains(self):
        cache = HistoryCache()
        self.assertIsNone(cache.get("missing"))
        self.assertNotIn("missing", cache)
        cache.get_or_create("obj-1")
        self.assertIn("obj-1", cache)
        self.assertEqual(cache.keys(), ["obj-1"])

    def test_iter_yields_histories(self):
        cache = HistoryCache()
        cache.get_or_create("a")
        cache.get_or_create("b")
        self.assertEqual({h.key for h in cache}, {"a", "b"})

    def test_remove(self):
        cache = HistoryCache()
        cache.get_or_create("obj-1")
        self.assertTrue(cache.remove("obj-1"))
        self.assertFalse(cache.remove("obj-1"))
        self.assertEqual(len(cache), 0)

    def test_clear_keeps_version(self):
        cache = HistoryCache()
        cache.get_or_create("a")
        cache.invalidate()
        cache.clear()
        self.assertEqual(len(cache), 0)
        self.assertEqual(cache.version, 1)

    def test_invalidate_bumps_version(self):
        cache = HistoryCache()
        self.assertEqual(cache.version, 0)
        self.assertEqual(cache.invalidate(), 1)
        self.assertEqual(cache.invalidate(), 2)


if __name__ == "__main__":
    unittest.main()
