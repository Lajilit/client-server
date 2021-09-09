import time
import unittest

from constants import *
from server import handle_message


class TestServer(unittest.TestCase):
    results = [
        {
            RESPONSE: 200
        },
        {
            RESPONSE: 400,
            ERROR: 'bad request'
        },
        {
            RESPONSE: 402,
            ERROR: 'no account with that name'
        }
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_handle_message_presence_ok(self):
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        self.assertEqual(handle_message(message), self.results[0])

    def test_handle_message_presence_no_user(self):
        message = {
            ACTION: 'wrong',
            TIME: time.time(),
            TYPE: STATUS
        }
        self.assertEqual(handle_message(message), self.results[1])

    def test_handle_message_presence_wrong_user(self):
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Wrong User',
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        self.assertEqual(handle_message(message), self.results[2])

    def test_handle_message_presence_no_action(self):
        message = {
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        self.assertEqual(handle_message(message), self.results[1])

    def test_handle_message_presence_wrong_action(self):
        message = {
            ACTION: 'wrong',
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: 'online'
            },
            TYPE: STATUS
        }

        self.assertEqual(handle_message(message), self.results[1])

    def test_handle_message_presence_no_time(self):
        message = {
            ACTION: PRESENCE,
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        self.assertEqual(handle_message(message), self.results[1])


if __name__ == '__main__':
    unittest.main()
