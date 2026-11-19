import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
from unittest.mock import ANY, Mock, call, mock_open, patch

import git

from rockstar import RockStar


class GitEnvironmentTests(unittest.TestCase):

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        with patch('os.getcwd', return_value=directory.name):
            self.rockstar = RockStar()

    def test_commit_dates_leave_the_caller_environment_unchanged(self):
        caller_dates = {
            'GIT_AUTHOR_DATE': '2020-01-02 03:04:05',
            'GIT_COMMITTER_DATE': '2020-02-03 04:05:06',
        }
        historical_date = datetime(2021, 3, 4, 5, 6, 7)
        current_date = datetime(2021, 5, 6, 7, 8, 9,
                                tzinfo=timezone(timedelta(hours=-4)))
        rockstar = self.rockstar
        repo = Mock()

        def verify_caller_dates(*args, **kwargs):
            self.assertEqual(dict(os.environ), caller_dates)

        repo.index.commit.side_effect = verify_caller_dates
        with patch.dict(os.environ, caller_dates, clear=True), \
                patch.object(git.Repo, 'init', return_value=repo), \
                patch.object(rockstar, '_get_dates_list',
                             return_value=[historical_date]), \
                patch('uuid.uuid1', return_value='test-marker'), \
                patch('rockstar.RockStar.open', mock_open(), create=True), \
                patch('rockstar.RockStar.datetime') as clock, \
                redirect_stdout(StringIO()):
            clock.now.return_value.astimezone.return_value = current_date
            rockstar.make_me_a_rockstar()
            self.assertEqual(dict(os.environ), caller_dates)

        self.assertEqual(repo.index.commit.call_args_list, [
            call(ANY, author_date='2021-03-04 05:06:07',
                 commit_date='2021-03-04 05:06:07'),
            call(ANY, author_date=current_date, commit_date=current_date),
        ])

    def test_failed_commit_does_not_leave_new_date_variables(self):
        rockstar = self.rockstar
        repo = Mock()
        repo.index.commit.side_effect = RuntimeError('commit failed')

        with patch.dict(os.environ, clear=True), \
                patch.object(git.Repo, 'init', return_value=repo), \
                patch.object(rockstar, '_get_dates_list',
                             return_value=[datetime(2021, 3, 4)]), \
                patch('uuid.uuid1', return_value='test-marker'), \
                patch('rockstar.RockStar.open', mock_open(), create=True), \
                redirect_stdout(StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'commit failed'):
                rockstar.make_me_a_rockstar()
            self.assertNotIn('GIT_AUTHOR_DATE', os.environ)
            self.assertNotIn('GIT_COMMITTER_DATE', os.environ)
