import importlib
import unittest
from unittest.mock import patch


rockstar_module = importlib.import_module('rockstar.RockStar')


class OffFractionTests(unittest.TestCase):
    def test_date_exclusion_uses_the_fraction_as_a_probability(self):
        cases = (
            (0.0, 0.0, 1, 1),
            (0.5, 0.499, 50, 0),
            (0.5, 0.5, 50, 1),
            (0.005, 0.004, 1, 0),
            (1.0, 0.9999999999999999, 100, 0),
        )

        for rate, draw, legacy_roll, expected_count in cases:
            with self.subTest(rate=rate, draw=draw):
                def integer_draw(minimum, maximum):
                    if (minimum, maximum) == (1, 100):
                        return legacy_roll
                    return minimum

                rockstar = rockstar_module.RockStar(days=1, off_fraction=rate)
                with patch.object(rockstar_module, 'random', return_value=draw, create=True), \
                        patch.object(rockstar_module, 'randint', side_effect=integer_draw):
                    dates = rockstar._get_dates_list()

                self.assertEqual(len(dates), expected_count)
