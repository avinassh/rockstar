#!/usr/bin/env python

import os
import sys
import uuid
from datetime import time, date, datetime, timedelta
from random import randint

import git
from progress.bar import Bar


hello_world_c = """#include <iostream>
int main()
{
  std::cout << "Hello World!";
}"""

default_file_name = 'main.cpp'


class RockStar:

    def __init__(self, days=400, file_name=default_file_name,
                 code=hello_world_c):
        self.days = days
        self.file_name = file_name
        self.file_path = os.path.join(os.getcwd(), file_name)
        self.code = code
        self.repo_path = os.getcwd()

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
        self.repo.index.commit(message)

    def _get_random_time(self):
        return time(hour=randint(0, 23), minute=randint(0, 59),
                    second=randint(0, 59), microsecond=randint(0, 999999))

    def _get_dates_list(self):
        today = date.today()
        dates_list = list()
        for day_delta in range(self.days):
            for i in range(randint(1, 10)):
                dates_list.append(today - timedelta(days=day_delta))
        yield from [
            datetime.combine(d, self._get_random_time())
            for d in dates_list
        ]

    def make_me_a_rockstar(self):
        self.repo = git.Repo.init(self.repo_path)
        progress_msg = 'Making you a Rockstar Programmer'
        bar = Bar(progress_msg, suffix='%(percent)d%%')
        for commit_date in bar.iter(self._get_dates_list()):
            self._edit_and_commit(str(uuid.uuid1()), commit_date)
        self._make_last_commit()
        print('\nYou are now a Rockstar Programmer!')
