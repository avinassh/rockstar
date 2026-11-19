import os
import tempfile
import unittest
from unittest.mock import patch

import git
from click.testing import CliRunner

from rockstar import RockStar, cli


class DestinationTests(unittest.TestCase):

    def test_rejects_an_existing_git_worktree_before_initializing(self):
        with tempfile.TemporaryDirectory() as directory:
            with git.Repo.init(directory):
                pass
            nested = os.path.join(directory, 'nested')
            os.mkdir(nested)
            literal = os.path.join(directory, '$ROCKSTAR_TEST_PATH')
            os.mkdir(literal)
            with patch.dict(os.environ, {'ROCKSTAR_TEST_PATH': 'missing'}):
                for path in (directory, nested, literal):
                    with self.subTest(path=path):
                        with patch('os.getcwd', return_value=path):
                            rockstar = RockStar()
                        with patch.object(
                            git.Repo, 'init',
                            side_effect=AssertionError('unexpected init'),
                        ):
                            with self.assertRaises(FileExistsError):
                                rockstar.make_me_a_rockstar()

    def test_cli_reports_that_it_needs_a_new_directory(self):
        runner = CliRunner()
        with tempfile.TemporaryDirectory() as directory:
            with git.Repo.init(directory):
                pass
            with patch('os.getcwd', return_value=directory):
                with patch.object(git.Repo, 'init',
                                  side_effect=AssertionError('unexpected init')):
                    result = runner.invoke(cli, [])

        self.assertEqual(result.exit_code, 1)
        self.assertIn('Error: Choose a new directory outside any Git repository.',
                      result.output)

    def test_a_directory_outside_a_git_worktree_can_be_initialized(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar(days=0)
            with patch.object(git.Repo, 'init') as init:
                with patch.object(rockstar, '_make_last_commit') as finish:
                    rockstar.make_me_a_rockstar()

            init.assert_called_once_with(rockstar.repo_path,
                                         expand_vars=False)
            finish.assert_called_once_with()
