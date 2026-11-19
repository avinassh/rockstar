from datetime import datetime
import os
import tempfile
import unittest
from unittest.mock import patch
import uuid

import git

from rockstar import RockStar


class PlaceholderTests(unittest.TestCase):
    def test_placeholder_uses_a_random_uuid(self):
        commit_date = datetime(2000, 1, 1)
        time_based_uuid = uuid.UUID('00000000-0000-1000-8000-000000000000')

        with tempfile.TemporaryDirectory() as directory:
            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar()
            with patch.object(rockstar, '_get_dates_list', return_value=[commit_date]), \
                    patch.object(git.Repo, 'init'), \
                    patch.object(rockstar, '_edit_and_commit') as edit_and_commit, \
                    patch.object(rockstar, '_make_last_commit'), \
                    patch.object(uuid, 'uuid1', return_value=time_based_uuid):
                rockstar.make_me_a_rockstar()

        placeholder = edit_and_commit.call_args[0][0]
        edit_and_commit.assert_called_once_with(placeholder, commit_date)
        parsed = uuid.UUID(placeholder)
        self.assertEqual(parsed.version, 4)
        self.assertEqual(placeholder, str(parsed))
