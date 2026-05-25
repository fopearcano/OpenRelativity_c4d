"""Unit tests for the pure-Python relativistic core (prototype approximations).

Run from the repository root with::

    python -m unittest openrelativity_c4d.tests.test_core_math
    # or simply:  python -m unittest

No Cinema 4D required.
"""

import math
import unittest

from openrelativity_c4d.core import doppler, relativity_math, searchlight, transforms


class TestArchitectureRules(unittest.TestCase):
    """Guard the hard constraint that the core never imports Cinema 4D."""

    def test_core_modules_do_not_import_c4d(self):
        for mod in (relativity_math, doppler, searchlight, transforms):
            self.assertFalse(
                hasattr(mod, "c4d"),
                "{0} must not import the c4d module".format(mod.__name__),
            )


class TestClampBeta(unittest.TestCase):
    def test_safe_max_below_one(self):
        self.assertLess(relativity_math.MAX_BETA, 1.0)

    def test_in_range_unchanged(self):
        self.assertEqual(relativity_math.clamp_beta(0.0), 0.0)
        self.assertEqual(relativity_math.clamp_beta(0.5), 0.5)
        self.assertEqual(relativity_math.clamp_beta(relativity_math.MAX_BETA),
                         relativity_math.MAX_BETA)

    def test_clamps_at_and_above_one(self):
        self.assertEqual(relativity_math.clamp_beta(1.0), relativity_math.MAX_BETA)
        self.assertEqual(relativity_math.clamp_beta(5.0), relativity_math.MAX_BETA)

    def test_negative_clamped_to_zero(self):
        self.assertEqual(relativity_math.clamp_beta(-0.3), 0.0)


class TestBetaFromSpeed(unittest.TestCase):
    def test_basic_ratio(self):
        self.assertAlmostEqual(relativity_math.beta_from_speed(100.0, 200.0), 0.5)
        self.assertAlmostEqual(relativity_math.beta_from_speed(0.0, 200.0), 0.0)

    def test_raw_value_can_exceed_one(self):
        # beta_from_speed is the raw ratio; clamping is a separate step.
        self.assertAlmostEqual(relativity_math.beta_from_speed(300.0, 200.0), 1.5)

    def test_degenerate_c_is_safe(self):
        self.assertEqual(relativity_math.beta_from_speed(50.0, 0.0),
                         relativity_math.MAX_BETA)


class TestGamma(unittest.TestCase):
    def test_gamma_at_rest_is_one(self):
        self.assertAlmostEqual(relativity_math.gamma_from_beta(0.0), 1.0)

    def test_gamma_known_value(self):
        self.assertAlmostEqual(relativity_math.gamma_from_beta(0.6), 1.25)

    def test_gamma_increases_with_beta(self):
        g0 = relativity_math.gamma_from_beta(0.0)
        g1 = relativity_math.gamma_from_beta(0.5)
        g2 = relativity_math.gamma_from_beta(0.9)
        self.assertLess(g0, g1)
        self.assertLess(g1, g2)

    def test_gamma_is_finite_and_clamped_past_c(self):
        g = relativity_math.gamma_from_beta(1.5)
        self.assertTrue(math.isfinite(g))
        self.assertAlmostEqual(g, relativity_math.gamma_from_beta(relativity_math.MAX_BETA))

    def test_inverse_gamma(self):
        self.assertAlmostEqual(relativity_math.inverse_gamma_from_beta(0.0), 1.0)
        self.assertAlmostEqual(relativity_math.inverse_gamma_from_beta(0.6), 0.8)


class TestLorentzContraction(unittest.TestCase):
    def test_no_contraction_at_rest(self):
        self.assertAlmostEqual(relativity_math.lorentz_contraction_scale(0.0, 1.0), 1.0)

    def test_known_value(self):
        self.assertAlmostEqual(relativity_math.lorentz_contraction_scale(0.6, 1.0), 0.8)

    def test_zero_strength_disables_effect(self):
        self.assertAlmostEqual(relativity_math.lorentz_contraction_scale(0.9, 0.0), 1.0)

    def test_scale_decreases_with_beta(self):
        s0 = relativity_math.lorentz_contraction_scale(0.0, 1.0)
        s1 = relativity_math.lorentz_contraction_scale(0.6, 1.0)
        s2 = relativity_math.lorentz_contraction_scale(0.9, 1.0)
        self.assertGreater(s0, s1)
        self.assertGreater(s1, s2)

    def test_scale_stays_in_unit_interval(self):
        for b in (0.0, 0.3, 0.6, 0.9, 1.5):
            s = relativity_math.lorentz_contraction_scale(b, 1.0)
            self.assertGreater(s, 0.0)
            self.assertLessEqual(s, 1.0)


class TestDoppler(unittest.TestCase):
    def test_no_shift_at_rest(self):
        self.assertAlmostEqual(doppler.doppler_factor(0.0, 1.0), 1.0)
        self.assertAlmostEqual(doppler.doppler_factor(0.0, -1.0), 1.0)

    def test_approaching_is_blueshift(self):
        factor = doppler.doppler_factor(0.6, 1.0)  # +1 = approaching
        self.assertAlmostEqual(factor, 0.5)
        self.assertTrue(doppler.is_blueshift(factor))

    def test_receding_is_redshift(self):
        factor = doppler.doppler_factor(0.6, -1.0)  # -1 = receding
        self.assertAlmostEqual(factor, 2.0)
        self.assertTrue(doppler.is_redshift(factor))

    def test_transverse_is_gamma(self):
        factor = doppler.doppler_factor(0.6, 0.0)
        self.assertAlmostEqual(factor, relativity_math.gamma_from_beta(0.6))

    def test_approaching_brighter_bluer_than_receding(self):
        self.assertLess(
            doppler.doppler_factor(0.7, 1.0), doppler.doppler_factor(0.7, -1.0)
        )

    def test_factor_always_positive_and_finite(self):
        for b in (0.0, 0.5, 0.9, 1.5):
            for ct in (-1.0, 0.0, 1.0):
                f = doppler.doppler_factor(b, ct)
                self.assertTrue(math.isfinite(f))
                self.assertGreater(f, 0.0)

    def test_cos_theta_is_clamped(self):
        self.assertAlmostEqual(
            doppler.doppler_factor(0.6, 5.0), doppler.doppler_factor(0.6, 1.0)
        )


class TestRgbDopplerShift(unittest.TestCase):
    def test_zero_strength_leaves_color_unchanged(self):
        base = (0.4, 0.5, 0.6)
        out = doppler.approximate_rgb_doppler_shift(base, factor=0.5, strength=0.0)
        for a, b in zip(out, base):
            self.assertAlmostEqual(a, b)

    def test_blueshift_cools_color(self):
        r, g, b = doppler.approximate_rgb_doppler_shift(
            (0.5, 0.5, 0.5), factor=0.5, strength=1.0
        )
        self.assertLess(r, 0.5)   # red pulled down
        self.assertGreater(b, 0.5)  # blue pushed up

    def test_redshift_warms_color(self):
        r, g, b = doppler.approximate_rgb_doppler_shift(
            (0.5, 0.5, 0.5), factor=2.0, strength=1.0
        )
        self.assertGreater(r, 0.5)  # red pushed up
        self.assertLess(b, 0.5)     # blue pulled down

    def test_output_always_clamped_0_1(self):
        cases = [
            ((2.0, -1.0, 0.5), 0.5, 1.0),   # out-of-range base
            ((1.0, 1.0, 1.0), 0.01, 5.0),   # extreme blueshift, big strength
            ((0.0, 0.0, 0.0), 50.0, 5.0),   # extreme redshift, big strength
            ((0.3, 0.7, 0.2), 1.0, 1.0),    # neutral factor
        ]
        for base, factor, strength in cases:
            out = doppler.approximate_rgb_doppler_shift(base, factor, strength)
            self.assertEqual(len(out), 3)
            for component in out:
                self.assertGreaterEqual(component, 0.0)
                self.assertLessEqual(component, 1.0)


class TestSearchlight(unittest.TestCase):
    def test_no_effect_at_rest(self):
        self.assertAlmostEqual(
            searchlight.searchlight_intensity_multiplier(0.0, 1.0, 1.0), 1.0
        )

    def test_zero_strength_disables_effect(self):
        self.assertAlmostEqual(
            searchlight.searchlight_intensity_multiplier(0.9, 1.0, 0.0), 1.0
        )

    def test_approaching_brightens(self):
        m = searchlight.searchlight_intensity_multiplier(0.6, 1.0, 1.0)
        self.assertAlmostEqual(m, 8.0)
        self.assertGreater(m, 1.0)

    def test_receding_dims(self):
        m = searchlight.searchlight_intensity_multiplier(0.6, -1.0, 1.0)
        self.assertAlmostEqual(m, 0.125)
        self.assertLess(m, 1.0)

    def test_extreme_case_remains_finite_and_clamped(self):
        m = searchlight.searchlight_intensity_multiplier(0.999, 1.0, 1.0)
        self.assertTrue(math.isfinite(m))
        self.assertLessEqual(m, searchlight.MAX_MULTIPLIER)
        self.assertGreaterEqual(m, searchlight.MIN_MULTIPLIER)


class TestTransforms(unittest.TestCase):
    def test_vector_helpers(self):
        self.assertAlmostEqual(transforms.dot((1, 2, 3), (4, 5, 6)), 32.0)
        self.assertEqual(transforms.add((1, 2, 3), (1, 1, 1)), (2, 3, 4))
        self.assertEqual(transforms.sub((1, 2, 3), (1, 1, 1)), (0, 1, 2))
        self.assertEqual(transforms.scale((1, 2, 3), 2), (2, 4, 6))
        self.assertAlmostEqual(transforms.length((3, 4, 0)), 5.0)

    def test_safe_normalize(self):
        self.assertEqual(transforms.safe_normalize((0, 0, 0)), (0.0, 0.0, 0.0))
        self.assertEqual(
            transforms.safe_normalize((0, 0, 0), fallback=(1.0, 0.0, 0.0)),
            (1.0, 0.0, 0.0),
        )
        _, ny, _ = transforms.safe_normalize((0, 3, 0))
        self.assertAlmostEqual(ny, 1.0)

    def test_add_velocity_zero_frame(self):
        self.assertEqual(
            transforms.add_velocity((0, 0, 0), (0.3, 0.0, 0.0)), (0.3, 0.0, 0.0)
        )

    def test_add_velocity_collinear(self):
        w = transforms.add_velocity((0.5, 0, 0), (0.5, 0, 0))
        self.assertAlmostEqual(w[0], 0.8)
        self.assertAlmostEqual(w[1], 0.0)
        self.assertAlmostEqual(w[2], 0.0)

    def test_add_velocity_perpendicular_stays_subluminal(self):
        w = transforms.add_velocity((0.6, 0, 0), (0.0, 0.6, 0.0))
        self.assertAlmostEqual(w[0], 0.6)
        self.assertAlmostEqual(w[1], 0.48)
        self.assertLess(transforms.length(w), 1.0)

    def test_apparent_position_static(self):
        pos, t = transforms.apparent_position((0, 0, 10), (0, 0, 0), c=1.0)
        self.assertAlmostEqual(t, -10.0)
        self.assertAlmostEqual(pos[2], 10.0)

    def test_apparent_position_moving(self):
        pos, t = transforms.apparent_position((0, 0, 10), (0, 0, -1), c=2.0)
        self.assertAlmostEqual(t, -10.0)
        self.assertAlmostEqual(pos[2], 20.0)
        self.assertAlmostEqual(transforms.length(pos), 2.0 * abs(t))


if __name__ == "__main__":
    unittest.main()
