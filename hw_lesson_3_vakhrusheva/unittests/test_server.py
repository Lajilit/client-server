import time
import unittest
import os, sys

sys.path.append(os.path.join(os.getcwd(), '..' ))

import common.constants as cnst
from server import handle_message


class TestServer(unittest.TestCase):
    results = [
        {
            cnst.RESPONSE: 200
        },
        {
            cnst.RESPONSE: 400,
            cnst.ERROR: 'bad request'
        },
        {
            cnst.RESPONSE: 402,
            cnst.ERROR: 'no account with that name'
        }
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_handle_message_presence_ok(self):
        message = {
            cnst.ACTION: cnst.PRESENCE,
            cnst.TIME: time.time(),
            cnst.USER: {
                cnst.ACCOUNT_NAME: 'Guest',
                cnst.STATUS: 'online'
            },
            cnst.TYPE: cnst.STATUS
        }
        self.assertEqual(handle_message(message), self.results[0])

    def test_handle_message_presence_no_user(self):
        message = {
            cnst.ACTION: 'wrong',
            cnst.TIME: time.time(),
            cnst.TYPE: cnst.STATUS
        }
        self.assertEqual(handle_message(message), self.results[1])

    def test_handle_message_presence_wrong_user(self):
        message = {
            cnst.ACTION: cnst.PRESENCE,
            cnst.TIME: time.time(),
            cnst.USER: {
                cnst.ACCOUNT_NAME: 'Wrong User',
                cnst.STATUS: 'online'
            },
            cnst.TYPE: cnst.STATUS
        }
        self.assertEqual(handle_message(message), self.results[2])

    def test_handle_message_presence_no_action(self):
        message = {
            cnst.TIME: time.time(),
            cnst.USER: {
                cnst.ACCOUNT_NAME: 'Guest',
                cnst.STATUS: 'online'
            },
            cnst.TYPE: cnst.STATUS
        }
        self.assertEqual(handle_message(message), self.results[1])

    def test_handle_message_presence_wrong_action(self):
        message = {
            cnst.ACTION: 'wrong',
            cnst.TIME: time.time(),
            cnst.USER: {
                cnst.ACCOUNT_NAME: 'Guest',
                cnst.STATUS: 'online'
            },
            cnst.TYPE: cnst.STATUS
        }

        self.assertEqual(handle_message(message), self.results[1])

    def test_handle_message_presence_no_time(self):
        message = {
            cnst.ACTION: cnst.PRESENCE,
            cnst.USER: {
                cnst.ACCOUNT_NAME: 'Guest',
                cnst.STATUS: 'online'
            },
            cnst.TYPE: cnst.STATUS
        }
        self.assertEqual(handle_message(message), self.results[1])


if __name__ == '__main__':
    unittest.main()
