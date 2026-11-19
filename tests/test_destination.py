import os
import tempfile
import unittest
from pathlib import Path
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

    def test_existing_output_is_rejected_before_initializing_git(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'main.cpp'
            output.write_bytes(b'existing file')
            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar()
            with patch.object(git.Repo, 'init',
                              side_effect=AssertionError('unexpected init')):
                with self.assertRaises(FileExistsError):
                    rockstar.make_me_a_rockstar()

            self.assertEqual(output.read_bytes(), b'existing file')

    def test_dangling_output_link_is_rejected_before_initializing_git(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'missing.cpp'
            output = Path(directory) / 'main.cpp'
            try:
                os.symlink(str(target), str(output))
            except (OSError, NotImplementedError, AttributeError):
                self.skipTest('symlinks are not available')

            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar()
            with patch.object(git.Repo, 'init',
                              side_effect=AssertionError('unexpected init')):
                with self.assertRaises(FileExistsError):
                    rockstar.make_me_a_rockstar()

            self.assertTrue(output.is_symlink())
            self.assertFalse(target.exists())

    def test_output_created_during_git_init_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'main.cpp'
            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar(days=0)

            def initialize(*args, **kwargs):
                output.write_bytes(b'other process output')

            with patch.object(git.Repo, 'init', side_effect=initialize):
                with patch.object(rockstar, '_make_last_commit') as finish:
                    with self.assertRaises(FileExistsError):
                        rockstar.make_me_a_rockstar()
                    finish.assert_not_called()

            self.assertEqual(output.read_bytes(), b'other process output')

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
