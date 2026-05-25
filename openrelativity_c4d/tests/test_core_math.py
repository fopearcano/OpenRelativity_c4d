"""Unit tests for the pure-Python relativistic core.

Run from the repository root with::

    python -m unittest openrelativity_c4d.tests.test_core_math
    # or simply:  python -m unittest

No Cinema 4D required.
"""

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


class TestRelativityMath(unittest.TestCase):
    def test_gamma_known_values(self):
        self.assertAlmostEqual(relativity_math.gamma_from_beta(0.0), 1.0)
        self.assertAlmostEqual(relativity_math.gamma_from_beta(0.6), 1.25)
        self.assertAlmostEqual(relativity_math.gamma_from_beta(0.8), 5.0 / 3.0)

    def test_gamma_diverges_at_or_above_c(self):
        with self.assertRaises(ValueError):
            relativity_math.gamma_from_beta(1.0)
        with self.assertRaises(ValueError):
            relativity_math.gamma_from_beta(1.5)

    def test_inverse_gamma(self):
        self.assertAlmostEqual(relativity_math.inverse_gamma_from_beta(0.6), 0.8)
        self.assertAlmostEqual(relativity_math.inverse_gamma_from_beta(0.8), 0.6)
        # Clamps to 0 at/above c instead of raising.
        self.assertEqual(relativity_math.inverse_gamma_from_beta(1.0), 0.0)
        self.assertEqual(relativity_math.inverse_gamma_from_beta(2.0), 0.0)

    def test_length_contraction(self):
        self.assertAlmostEqual(relativity_math.contract_length(10.0, 0.0), 10.0)
        self.assertAlmostEqual(relativity_math.contract_length(10.0, 0.6), 8.0)

    def test_time_dilation(self):
        self.assertAlmostEqual(relativity_math.dilate_time(1.0, 0.6), 1.25)

    def test_collinear_velocity_addition(self):
        # c = 1
        self.assertAlmostEqual(relativity_math.add_velocities_collinear(0.5, 0.5), 0.8)
        # Adding the speed of light returns the speed of light.
        self.assertAlmostEqual(relativity_math.add_velocities_collinear(1.0, 0.5), 1.0)
        # OpenRelativity-style low c.
        self.assertAlmostEqual(
            relativity_math.add_velocities_collinear(100.0, 100.0, c=200.0), 160.0
        )


class TestDoppler(unittest.TestCase):
    def test_no_shift_at_rest(self):
        self.assertAlmostEqual(doppler.doppler_shift(0.0, 1.0), 1.0)
        self.assertAlmostEqual(doppler.doppler_shift(0.0, -1.0), 1.0)

    def test_approaching_is_blueshift(self):
        shift = doppler.doppler_shift(0.6, 1.0)  # head-on approach
        self.assertAlmostEqual(shift, 0.5)
        self.assertTrue(doppler.is_blueshift(shift))

    def test_receding_is_redshift(self):
        shift = doppler.doppler_shift(0.6, -1.0)  # head-on recession
        self.assertAlmostEqual(shift, 2.0)
        self.assertTrue(doppler.is_redshift(shift))

    def test_transverse_doppler_is_gamma(self):
        shift = doppler.doppler_shift(0.6, 0.0)
        self.assertAlmostEqual(shift, relativity_math.gamma_from_beta(0.6))
        self.assertTrue(doppler.is_redshift(shift))

    def test_invalid_beta(self):
        with self.assertRaises(ValueError):
            doppler.doppler_shift(1.0, 0.0)


class TestSearchlight(unittest.TestCase):
    def test_known_values(self):
        self.assertAlmostEqual(searchlight.searchlight_intensity(1.0), 1.0)
        self.assertAlmostEqual(searchlight.searchlight_intensity(0.5), 8.0)
        self.assertAlmostEqual(searchlight.searchlight_intensity(2.0), 0.125)

    def test_blueshift_brightens_redshift_dims(self):
        self.assertGreater(searchlight.searchlight_intensity(0.5), 1.0)
        self.assertLess(searchlight.searchlight_intensity(2.0), 1.0)

    def test_invalid_shift(self):
        with self.assertRaises(ValueError):
            searchlight.searchlight_intensity(0.0)


class TestTransforms(unittest.TestCase):
    def test_vector_helpers(self):
        self.assertAlmostEqual(transforms.dot((1, 2, 3), (4, 5, 6)), 32.0)
        self.assertEqual(transforms.add((1, 2, 3), (1, 1, 1)), (2, 3, 4))
        self.assertEqual(transforms.sub((1, 2, 3), (1, 1, 1)), (0, 1, 2))
        self.assertEqual(transforms.scale((1, 2, 3), 2), (2, 4, 6))
        self.assertAlmostEqual(transforms.length((3, 4, 0)), 5.0)
        self.assertEqual(transforms.normalize((0, 0, 0)), (0.0, 0.0, 0.0))
        nx, ny, nz = transforms.normalize((0, 3, 0))
        self.assertAlmostEqual(ny, 1.0)

    def test_add_velocity_zero_frame(self):
        self.assertEqual(
            transforms.add_velocity((0, 0, 0), (0.3, 0.0, 0.0)), (0.3, 0.0, 0.0)
        )

    def test_add_velocity_collinear_matches_scalar(self):
        w = transforms.add_velocity((0.5, 0, 0), (0.5, 0, 0))
        self.assertAlmostEqual(w[0], 0.8)
        self.assertAlmostEqual(w[1], 0.0)
        self.assertAlmostEqual(w[2], 0.0)

    def test_add_velocity_perpendicular(self):
        # v along x, u along y: perpendicular component scaled by 1/gamma = 0.8.
        w = transforms.add_velocity((0.6, 0, 0), (0.0, 0.6, 0.0))
        self.assertAlmostEqual(w[0], 0.6)
        self.assertAlmostEqual(w[1], 0.48)
        self.assertAlmostEqual(w[2], 0.0)
        self.assertLess(transforms.length(w), 1.0)  # still sub-luminal

    def test_apparent_position_static(self):
        pos, t = transforms.apparent_position((0, 0, 10), (0, 0, 0), c=1.0)
        self.assertAlmostEqual(t, -10.0)  # light left 10 time-units ago
        self.assertAlmostEqual(pos[2], 10.0)  # static -> seen where it is

    def test_apparent_position_static_with_custom_c(self):
        _, t = transforms.apparent_position((0, 0, 10), (0, 0, 0), c=2.0)
        self.assertAlmostEqual(t, -5.0)

    def test_apparent_position_moving(self):
        pos, t = transforms.apparent_position((0, 0, 10), (0, 0, -1), c=2.0)
        self.assertAlmostEqual(t, -10.0)
        self.assertAlmostEqual(pos[2], 20.0)
        # Retarded distance equals c * |t|.
        self.assertAlmostEqual(transforms.length(pos), 2.0 * abs(t))

    def test_apparent_time_offset_at_lightspeed(self):
        # |v| == c exercises the linear-equation branch (a == 0).
        t = transforms.apparent_time_offset((0, 0, 10), (0, 0, 1), c=1.0)
        self.assertAlmostEqual(t, -5.0)


if __name__ == "__main__":
    unittest.main()
