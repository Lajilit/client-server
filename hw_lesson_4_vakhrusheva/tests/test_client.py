import time
import unittest
import os, sys

sys.path.append(os.path.join(os.getcwd(), ''))

from  common.constants import *
from client import create_presence_message, handle_response

class TestClient(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_presence_message_default_user(self):
        message = create_presence_message()
        result = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        self.assertEqual(message, result)

    def test_create_presence_message_user(self):
        message = create_presence_message('User')
        result = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: 'User',
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        self.assertEqual(message, result)

    def test_handle_response_200(self):
        message = {
            RESPONSE: 200
        }
        result = '200 : OK'
        self.assertEqual(handle_response(message), result)

    def test_handle_response_400(self):
        message = {
            RESPONSE: 400,
            ERROR: 'bad request'
        }
        result = '400 : bad request'
        self.assertEqual(handle_response(message), result)

    def test_handle_response_402(self):
        message = {
            RESPONSE: 402,
            ERROR: 'no account with that name'
        }
        result = '402 : no account with that name'
        self.assertEqual(handle_response(message), result)

    def test_handle_response_error(self):
        message = {
        }
        self.assertRaises(ValueError, handle_response, message)


if __name__ == '__main__':
    unittest.main()
