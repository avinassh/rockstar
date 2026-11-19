import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

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

    def test_invalid_output_paths_do_not_open_or_initialize_git(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'work'
            root.mkdir()
            sibling = Path(directory) / 'work-other'
            sibling.mkdir()
            (root / 'file-parent').touch()
            cases = (
                (str(sibling / 'output.cpp'), 'inside the working directory'),
                ('missing/output.cpp', 'existing parent directory'),
                ('missing/../output.cpp', 'existing parent directory'),
                ('file-parent/output.cpp', 'existing parent directory'),
                ('missing-output/', 'valid output filename'),
                ('invalid\x00.cpp', 'valid output filename'),
                ('nested/.GiT/output.cpp', 'Git metadata'),
            )
            for filename, error in cases:
                with self.subTest(filename=filename):
                    with patch('os.getcwd', return_value=str(root)):
                        rockstar = RockStar(days=0, file_name=filename)
                    with patch('git.Repo') as repo, \
                            patch('rockstar.RockStar.open', create=True) as output:
                        repo.side_effect = AssertionError('unexpected Git lookup')
                        with self.assertRaisesRegex(ValueError, error):
                            rockstar.make_me_a_rockstar()
                        repo.assert_not_called()
                        repo.init.assert_not_called()
                        output.assert_not_called()

    def test_linked_output_parents_are_validated_before_initializing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'work'
            root.mkdir()
            sibling = Path(directory) / 'other'
            sibling.mkdir()
            metadata = root / '.GiT'
            metadata.mkdir()
            target = root / 'nested' / 'child'
            target.mkdir(parents=True)
            try:
                os.symlink(str(sibling), str(root / 'outer-link'))
                os.symlink(str(metadata), str(root / 'metadata-link'))
                os.symlink(str(target), str(root / 'nested-link'))
            except (OSError, NotImplementedError, AttributeError):
                self.skipTest('symlinks are not available')

            cases = (
                ('outer-link/output.cpp', 'inside the working directory'),
                ('metadata-link/output.cpp', 'Git metadata'),
                ('nested-link/../output.cpp', 'unambiguous output directory'),
            )
            for filename, error in cases:
                with self.subTest(filename=filename):
                    with patch('os.getcwd', return_value=str(root)):
                        rockstar = RockStar(days=0, file_name=filename)
                    with patch('git.Repo') as repo, \
                            patch('rockstar.RockStar.open', create=True) as output:
                        repo.side_effect = AssertionError('unexpected Git lookup')
                        with self.assertRaisesRegex(ValueError, error):
                            rockstar.make_me_a_rockstar()
                        repo.assert_not_called()
                        repo.init.assert_not_called()
                        output.assert_not_called()

    def test_output_inside_a_nested_git_worktree_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            nested = Path(directory) / 'nested'
            nested.mkdir()
            with git.Repo.init(str(nested)):
                pass
            parent = nested / 'child'
            parent.mkdir()
            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar(days=0, file_name='nested/child/output.cpp')
            with patch.object(
                    git.Repo, 'init',
                    side_effect=AssertionError('unexpected init')), \
                    patch('rockstar.RockStar.open', create=True) as output:
                with self.assertRaisesRegex(FileExistsError, 'Git repository'):
                    rockstar.make_me_a_rockstar()
                output.assert_not_called()

    def test_in_tree_relative_and_absolute_output_paths_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory) / 'nested'
            parent.mkdir()
            for filename in ('nested/relative.cpp', str(parent / 'absolute.cpp')):
                with self.subTest(filename=filename):
                    with patch('os.getcwd', return_value=directory):
                        rockstar = RockStar(days=0, file_name=filename)
                    with patch.object(git.Repo, 'init') as init, \
                            patch('rockstar.RockStar.open', mock_open(),
                                  create=True) as output, \
                            patch.object(rockstar, '_make_last_commit') as finish:
                        rockstar.make_me_a_rockstar()
                    init.assert_called_once_with(directory, expand_vars=False)
                    output.assert_called_once_with(rockstar.file_path, 'x')
                    self.assertEqual(finish.call_count, 1)

    def test_in_tree_linked_parent_preserves_the_original_output_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'work'
            parent = root / 'nested'
            parent.mkdir(parents=True)
            targets = [parent]
            alternate = root.with_name('WORK') / 'nested'
            if alternate.is_dir() and alternate.samefile(parent):
                targets.append(alternate)

            for index, target in enumerate(targets):
                with self.subTest(target=target):
                    link = root / ('in-tree-link-{}'.format(index))
                    try:
                        os.symlink(str(target), str(link))
                    except (OSError, NotImplementedError, AttributeError):
                        self.skipTest('symlinks are not available')

                    filename = os.path.join(link.name, 'output.cpp')
                    with patch('os.getcwd', return_value=str(root)):
                        rockstar = RockStar(days=0, file_name=filename)
                    with patch.object(git.Repo, 'init') as init, \
                            patch('rockstar.RockStar.open', mock_open(),
                                  create=True) as output, \
                            patch.object(rockstar, '_make_last_commit') as finish:
                        rockstar.make_me_a_rockstar()

                    init.assert_called_once_with(str(root), expand_vars=False)
                    output.assert_called_once_with(str(root / filename), 'x')
                    self.assertEqual(finish.call_count, 1)

    def test_link_into_a_nested_git_worktree_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / 'nested'
            nested.mkdir()
            try:
                os.symlink(str(nested), str(root / 'nested-link'))
            except (OSError, NotImplementedError, AttributeError):
                self.skipTest('symlinks are not available')
            with git.Repo.init(str(nested)):
                pass

            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar(days=0, file_name='nested-link/output.cpp')
            with patch.object(
                    git.Repo, 'init',
                    side_effect=AssertionError('unexpected init')), \
                    patch('rockstar.RockStar.open', create=True) as output:
                with self.assertRaisesRegex(FileExistsError, 'Git repository'):
                    rockstar.make_me_a_rockstar()
                output.assert_not_called()

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

    def test_rejects_git_location_overrides_before_git_or_output(self):
        rockstar = RockStar(days=0)
        for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR',
                     'GIT_OBJECT_DIRECTORY'):
            for value in ('', 'caller-location'):
                overrides = {name: value}
                with self.subTest(name=name, value=value), \
                        patch.dict(os.environ, overrides, clear=True), \
                        patch('git.Repo') as repo, \
                        patch('rockstar.RockStar.open', create=True) as output:
                    repo.side_effect = AssertionError('unexpected Git lookup')
                    with self.assertRaisesRegex(ValueError, name):
                        rockstar.make_me_a_rockstar()
                    repo.assert_not_called()
                    repo.init.assert_not_called()
                    output.assert_not_called()
                    self.assertEqual(dict(os.environ), overrides)

    def test_cli_shows_git_location_variable_names_without_their_values(self):
        overrides = {
            'GIT_WORK_TREE': 'caller-worktree',
            'GIT_DIR': 'caller-git-directory',
        }
        with patch.dict(os.environ, overrides), \
                patch.object(RockStar, '_load_commit_messages'), \
                patch('git.Repo') as repo, \
                patch('rockstar.RockStar.open', create=True) as output:
            repo.side_effect = AssertionError('unexpected Git lookup')
            result = CliRunner().invoke(cli, ['--days', '0'])
            repo.assert_not_called()
            repo.init.assert_not_called()
            output.assert_not_called()
            for name, value in overrides.items():
                self.assertEqual(os.environ[name], value)

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(
            result.output,
            'Error: Unset these Git location variables before running Rockstar '
            '(GIT_DIR, GIT_WORK_TREE).\n',
        )

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
            author_env = {'GIT_AUTHOR_DATE': '2021-01-01 00:00:00'}
            with patch.dict(os.environ, author_env, clear=True), \
                    patch.object(git.Repo, 'init') as init, \
                    patch.object(rockstar, '_make_last_commit') as finish:
                rockstar.make_me_a_rockstar()
                self.assertEqual(dict(os.environ), author_env)

            init.assert_called_once_with(rockstar.repo_path,
                                         expand_vars=False)
            finish.assert_called_once_with()
