from datetime import date
import importlib
import unittest
from unittest.mock import patch


rockstar_module = importlib.import_module('rockstar.RockStar')


class LocalizedDate(date):
    @classmethod
    def today(cls):
        return cls(2024, 1, 2)

    def strftime(self, format):
        if format == '%A':
            return {0: 'Montag', 1: 'Dienstag'}[self.weekday()]
        return super().strftime(format)


class WeekdayLocaleTests(unittest.TestCase):
    def test_skips_english_and_localized_weekday_names(self):
        cases = (
            ('mOnDaY', date(2024, 1, 2)),
            ('mOnTaG', date(2024, 1, 2)),
            ('Tuesday', date(2024, 1, 1)),
            ('Dienstag', date(2024, 1, 1)),
        )

        with patch.object(rockstar_module, 'date', LocalizedDate), \
                patch.object(rockstar_module, 'randint', return_value=1):
            for weekday, expected in cases:
                with self.subTest(weekday=weekday):
                    rockstar = rockstar_module.RockStar(days=2, days_off=[weekday])
                    planned_dates = [entry.date() for entry in rockstar._get_dates_list()]
                    self.assertEqual(planned_dates, [expected])
