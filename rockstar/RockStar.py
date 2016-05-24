#!/usr/bin/env python

import os
import uuid
import json
from datetime import time, date, datetime, timedelta
from random import randint
from random import choice

import click
import git

HELLO_WORLD_C = """#include <iostream>
int main()
{
  std::cout << "Hello World!" << std::endl;
  return 0;
}
"""

DEFAULT_FILE_NAME = 'main.cpp'


class RockStar:

    def __init__(self, days=400, days_off=(), file_name=DEFAULT_FILE_NAME,
                 code=HELLO_WORLD_C, off_fraction=0.0):
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
        def dates():
            today = date.today()
            for day_delta in range(self.days):
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
        self.repo = git.Repo.init(self.repo_path)
        label = 'Making you a Rockstar Programmer'
        with click.progressbar(self._get_dates_list(), label=label) as bar:
            for commit_date in bar:
                self._edit_and_commit(str(uuid.uuid1()), commit_date)
        self._make_last_commit()
        print('\nYou are now a Rockstar Programmer!')


@click.command()
@click.option('--days', type=int, default=400)
def cli(days):
    magic = RockStar(days=days)
    magic.make_me_a_rockstar()
