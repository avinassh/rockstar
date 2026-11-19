#!/usr/bin/env python

import operator
import os
import uuid
import json
from datetime import time, date, datetime, timedelta
from random import randint
from random import choice
from pathlib import Path

import click
import git

HELLO_WORLD_CPP = """#include <iostream>
int main()
{
  std::cout << "Hello World!" << std::endl;
  return 0;
}
"""

DEFAULT_FILE_NAME = 'main.cpp'
_GIT_LOCATION_VARIABLES = (
    'GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_OBJECT_DIRECTORY',
)


class _GitLocationError(ValueError):
    pass


class _OutputPathError(ValueError):
    pass


def _check_output_location(path, root):
    try:
        relative = path.relative_to(root)
    except ValueError:
        raise _OutputPathError(
            'Choose an output file inside the working directory.') from None

    if any(part.lower() == '.git' for part in relative.parts):
        raise _OutputPathError('Choose an output path outside Git metadata.')


def _resolve_output_parent(work_directory, file_path):
    if '\0' in file_path:
        raise _OutputPathError('Choose a valid output filename.')
    if os.path.lexists(file_path):
        raise FileExistsError(
            'Output file already exists: {}'.format(file_path))
    if not os.path.basename(file_path):
        raise _OutputPathError('Choose a valid output filename.')

    root = Path(os.path.abspath(work_directory))
    normalized_output = Path(os.path.abspath(file_path))
    _check_output_location(normalized_output, root)

    parent_error = 'Choose an output file with an existing parent directory.'
    try:
        parent = Path(file_path).parent
        if not parent.is_dir():
            raise _OutputPathError(parent_error)
        # GitPython normalizes the path before adding it to the index.
        if not parent.samefile(normalized_output.parent):
            raise _OutputPathError('Choose an unambiguous output directory.')

        parent = parent.resolve()
        resolved_root = root.resolve()
        parent_root = Path(*parent.parts[:len(resolved_root.parts)])
        if not parent_root.samefile(resolved_root):
            raise _OutputPathError(
                'Choose an output file inside the working directory.')
    except (OSError, RuntimeError):
        raise _OutputPathError(parent_error) from None

    _check_output_location(parent, parent_root)
    return str(parent)


def _validate_day_count(days, today):
    days = operator.index(days)
    max_days = today.toordinal()
    if not 0 <= days <= max_days:
        raise ValueError('Choose a day count from 0 to {}.'.format(max_days))
    return days


class RockStar:

    def __init__(self, days=400, days_off=(), file_name=DEFAULT_FILE_NAME,
                 code=HELLO_WORLD_CPP, off_fraction=0.0):
        self.repo = None
        self.days = days
        self.file_name = file_name
        self.file_path = os.path.join(os.getcwd(), file_name)
        self.code = code
        self.repo_path = os.getcwd()
        self.messages_file_name = 'commit-messages.json'
        self.messages_file_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), self.messages_file_name)
        self.days_off = list(map(str.capitalize, days_off))
        self.off_fraction = off_fraction

        self._load_commit_messages()

    def _load_commit_messages(self):
        with open(self.messages_file_path) as f:
            messages_file_contents = json.load(f)
        names = messages_file_contents['names']
        messages = messages_file_contents['messages']
        self.commit_messages = [m.format(name=choice(names)) for m in messages]

    def _get_random_commit_message(self):
        return choice(self.commit_messages)

    def _make_last_commit(self):
        with open(self.file_path, 'w') as f:
            f.write(self.code)

        os.environ['GIT_AUTHOR_DATE'] = ''
        os.environ['GIT_COMMITTER_DATE'] = ''
        self.repo.index.add([self.file_path])
        self.repo.index.commit('Final commit :sunglasses:')

    def _edit_and_commit(self, message, commit_date):
        with open(self.file_path, 'w') as f:
            f.write(message)
        self.repo.index.add([self.file_path])
        date_in_iso = commit_date.strftime("%Y-%m-%d %H:%M:%S")
        os.environ['GIT_AUTHOR_DATE'] = date_in_iso
        os.environ['GIT_COMMITTER_DATE'] = date_in_iso
        self.repo.index.commit(self._get_random_commit_message())

    @staticmethod
    def _get_random_time():
        return time(hour=randint(0, 23), minute=randint(0, 59),
                    second=randint(0, 59), microsecond=randint(0, 999999))

    def _get_dates_list(self):
        today = date.today()
        days = _validate_day_count(self.days, today)

        def dates():
            for day_delta in range(days):
                day = today - timedelta(days=day_delta)
                if day.strftime('%A') in self.days_off:
                    continue
                if randint(1, 100) < self.off_fraction * 100:
                    continue
                for i in range(randint(1, 10)):
                    yield day
        return [datetime.combine(d, self._get_random_time())
                for d in dates()]

    def make_me_a_rockstar(self):
        git_location_variables = [
            name for name in _GIT_LOCATION_VARIABLES if name in os.environ
        ]
        if git_location_variables:
            names = ', '.join(git_location_variables)
            raise _GitLocationError(
                'Unset these Git location variables before running Rockstar '
                '({}).'.format(names))

        output_parent = _resolve_output_parent(self.repo_path, self.file_path)
        try:
            existing_repo = git.Repo(
                output_parent, search_parent_directories=True,
                expand_vars=False)
        except git.InvalidGitRepositoryError:
            pass
        else:
            existing_repo.close()
            raise FileExistsError(
                'Choose a new directory outside any Git repository.')

        commit_dates = self._get_dates_list()
        self.repo = git.Repo.init(self.repo_path, expand_vars=False)
        # Refuse files created since the earlier check before writing output.
        with open(self.file_path, 'x'):
            pass

        label = 'Making you a Rockstar Programmer'
        with click.progressbar(commit_dates, label=label) as bar:
            for commit_date in bar:
                self._edit_and_commit(str(uuid.uuid1()), commit_date)
        self._make_last_commit()
        print('\nYou are now a Rockstar Programmer!')


def _validate_days_option(_context, _parameter, value):
    try:
        return _validate_day_count(value, date.today())
    except ValueError as error:
        raise click.BadParameter(str(error)) from error


@click.command()
@click.option('--days', type=int, default=400, callback=_validate_days_option)
def cli(days):
    magic = RockStar(days=days)
    try:
        magic.make_me_a_rockstar()
    except (FileExistsError, _GitLocationError, _OutputPathError) as error:
        raise click.ClickException(str(error)) from error
