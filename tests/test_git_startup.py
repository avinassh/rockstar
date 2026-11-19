import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from textwrap import dedent
from unittest.mock import patch

import git
from click.testing import CliRunner

from rockstar import RockStar, cli


class GitStartupTests(unittest.TestCase):

    def run_without_git(self, script, mode='error', args=()):
        with tempfile.TemporaryDirectory() as directory:
            env = os.environ.copy()
            for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR',
                         'GIT_OBJECT_DIRECTORY', 'PYTHONOPTIMIZE'):
                env.pop(name, None)
            env.update(
                PATH=directory,
                PYTHONPATH=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                PYTHONDONTWRITEBYTECODE='1',
                GIT_PYTHON_GIT_EXECUTABLE=os.path.join(directory, 'missing-git'),
                GIT_PYTHON_REFRESH=mode,
            )
            result = subprocess.run(
                [sys.executable, '-c', dedent(script)] + list(args),
                cwd=directory, env=env, universal_newlines=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_help_and_constructor_do_not_require_git(self):
        self.run_without_git("""
            import sys
            from click.testing import CliRunner
            from rockstar import RockStar, cli

            result = CliRunner().invoke(cli, ['--help'])
            assert result.exit_code == 0, result.output
            assert '--days' in result.output, result.output
            assert RockStar(days=0).repo is None
            assert 'git' not in sys.modules
        """)

    def test_missing_git_reports_a_clear_error_without_writing_output(self):
        for mode in ('error', 'quiet'):
            with self.subTest(mode=mode):
                self.run_without_git("""
                    import os
                    from click.testing import CliRunner
                    from rockstar import cli

                    result = CliRunner().invoke(cli, ['--days', '0'])
                    assert result.exit_code == 1, result.output
                    assert result.output == (
                        'Error: Install Git or set GIT_PYTHON_GIT_EXECUTABLE '
                        'to the path of a working Git executable.\\n'
                    ), result.output
                    assert os.listdir('.') == []
                    assert os.environ['GIT_PYTHON_GIT_EXECUTABLE'].endswith(
                        'missing-git'
                    )
                """, mode=mode)

    def test_quiet_failure_can_retry_and_keep_configured_git(self):
        executable = shutil.which('git')
        if executable is None:
            self.skipTest('Git executable is required for the recovery check')

        self.run_without_git("""
            import os
            import sys
            from unittest.mock import mock_open, patch

            import git
            from click.testing import CliRunner
            from rockstar import RockStar, cli

            result = CliRunner().invoke(cli, ['--days', '0'])
            assert result.exit_code == 1
            assert not git.GIT_OK
            invalid_executable = os.environ['GIT_PYTHON_GIT_EXECUTABLE']
            os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = sys.argv[1]

            rockstar = RockStar(days=0)
            with patch.object(git.Repo, 'init') as init, \\
                    patch('rockstar.RockStar.open', mock_open(), create=True), \\
                    patch.object(rockstar, '_make_last_commit') as finish:
                rockstar.make_me_a_rockstar()
                assert init.call_count == 1
                assert finish.call_count == 1
            assert git.GIT_OK

            git.refresh(sys.argv[1])
            os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = invalid_executable
            with patch.object(git.Repo, 'init') as init, \\
                    patch('rockstar.RockStar.open', mock_open(), create=True), \\
                    patch.object(rockstar, '_make_last_commit'), \\
                    patch.object(git, 'refresh', side_effect=AssertionError):
                rockstar.make_me_a_rockstar()
                assert init.call_count == 1
            assert os.listdir('.') == []
        """, mode='quiet', args=(os.path.abspath(executable),))

    def test_missing_git_after_import_is_reported_before_output(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('os.getcwd', return_value=directory), \
                    patch.object(
                        git.Repo, 'init',
                        side_effect=git.GitCommandNotFound('git', 'not found')):
                result = CliRunner().invoke(cli, ['--days', '0'])
            self.assertEqual(os.listdir(directory), [])

        self.assertEqual(result.exit_code, 1)
        self.assertIn('Error: Install Git', result.output)

    def test_unrelated_import_errors_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch('os.getcwd', return_value=directory):
                rockstar = RockStar(days=0)
            real_import = __import__

            def import_with_broken_dependency(name, *args, **kwargs):
                if name == 'git':
                    raise ImportError('Unable to import gitdb')
                return real_import(name, *args, **kwargs)

            with patch('builtins.__import__', import_with_broken_dependency), \
                    patch.object(git.Repo, 'init',
                                 side_effect=AssertionError('unexpected init')), \
                    patch('rockstar.RockStar.open', create=True) as output:
                with self.assertRaisesRegex(ImportError, 'Unable to import gitdb'):
                    rockstar.make_me_a_rockstar()
                output.assert_not_called()
