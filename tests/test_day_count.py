import unittest
from contextlib import ExitStack, redirect_stdout
from datetime import date, datetime
from io import StringIO
from unittest.mock import call, patch

import git
from click.testing import CliRunner

from rockstar import RockStar, cli


class IndexedDayCount:
    def __init__(self):
        self.calls = 0

    def __index__(self):
        self.calls += 1
        return 2


class DayCountTests(unittest.TestCase):
    def setUp(self):
        mocks = ExitStack()
        self.addCleanup(mocks.close)

        clock = mocks.enter_context(patch('rockstar.RockStar.date'))
        self.today = clock.today
        self.today.return_value = date(1, 1, 2)
        mocks.enter_context(patch('rockstar.RockStar.randint', return_value=1))
        mocks.enter_context(patch('uuid.uuid1', return_value='placeholder'))
        mocks.enter_context(patch('uuid.uuid4', return_value='placeholder'))
        self.repo = mocks.enter_context(
            patch('rockstar.RockStar.git.Repo',
                  side_effect=git.InvalidGitRepositoryError))
        self.load_messages = mocks.enter_context(
            patch.object(RockStar, '_load_commit_messages'))
        self.output = mocks.enter_context(
            patch('rockstar.RockStar.open', create=True))
        self.edit = mocks.enter_context(
            patch.object(RockStar, '_edit_and_commit'))
        self.finish = mocks.enter_context(
            patch.object(RockStar, '_make_last_commit'))

    def reset_effects(self):
        for effect in (self.repo, self.load_messages, self.output,
                       self.edit, self.finish):
            effect.reset_mock()

    def test_invalid_day_count_stops_before_initialization_or_output(self):
        for value, error_type in (
                (-1, ValueError), (3, ValueError), (10 ** 100, ValueError),
                (1.5, TypeError), ('1', TypeError)):
            with self.subTest(days=value):
                self.reset_effects()
                with self.assertRaises(error_type), redirect_stdout(StringIO()):
                    RockStar(days=value).make_me_a_rockstar()
                self.repo.init.assert_not_called()
                self.output.assert_not_called()
                self.edit.assert_not_called()
                self.finish.assert_not_called()

    def test_zero_days_still_performs_the_final_step_only(self):
        rockstar = RockStar(days=0)
        with redirect_stdout(StringIO()):
            rockstar.make_me_a_rockstar()

        self.repo.init.assert_called_once()
        self.edit.assert_not_called()
        self.finish.assert_called_once()

    def test_indexable_days_can_reach_the_first_calendar_day(self):
        days = IndexedDayCount()
        with redirect_stdout(StringIO()):
            RockStar(days=days).make_me_a_rockstar()

        self.assertEqual(days.calls, 1)
        self.today.assert_called_once()
        self.assertEqual(self.edit.call_args_list, [
            call('placeholder', datetime(1, 1, 2, 1, 1, 1, 1)),
            call('placeholder', datetime(1, 1, 1, 1, 1, 1, 1)),
        ])
        self.finish.assert_called_once()

    def test_cli_reports_invalid_days_before_initializing(self):
        runner = CliRunner()
        for value in ('-1', '3', '1.5'):
            with self.subTest(days=value):
                self.reset_effects()
                result = runner.invoke(cli, ['--days=' + value])
                self.assertEqual(result.exit_code, 2)
                self.assertIn('--days', result.output)
                self.repo.assert_not_called()
                self.repo.init.assert_not_called()
                self.output.assert_not_called()
                self.load_messages.assert_not_called()
