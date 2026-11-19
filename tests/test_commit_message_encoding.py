import importlib
import json
import unittest
from unittest.mock import patch


rockstar_module = importlib.import_module('rockstar.RockStar')


def open_with_ascii_default(path, mode='r', *, encoding='ascii'):
    return open(path, mode, encoding=encoding)


class CommitMessageEncodingTests(unittest.TestCase):
    def test_reads_packaged_commit_messages_with_an_ascii_default(self):
        with patch.object(
            rockstar_module, 'open', open_with_ascii_default, create=True
        ), patch.object(rockstar_module, 'choice', side_effect=lambda names: names[0]):
            rockstar = rockstar_module.RockStar()

        with open(rockstar.messages_file_path, encoding='utf-8') as messages_file:
            asset = json.load(messages_file)
        expected = [
            message.format(name=asset['names'][0]) for message in asset['messages']
        ]

        self.assertTrue(any(ord(char) > 127 for message in expected for char in message))
        self.assertEqual(rockstar.commit_messages, expected)
