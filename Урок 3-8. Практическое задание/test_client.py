import time
import unittest

import common.constants as cnst
from client import create_presence_message, handle_response


class TestClient(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_presence_message_default_user(self):
        message = create_presence_message()
        result = {
            cnst.ACTION: cnst.PRESENCE,
            cnst.TIME: time.time(),
            cnst.USER: {
                cnst.ACCOUNT_NAME: 'Guest',
                cnst.STATUS: 'online'
            },
            cnst.TYPE: cnst.STATUS
        }
        self.assertEqual(message, result)

    def test_create_presence_message_user(self):
        message = create_presence_message('User')
        result = {
            cnst.ACTION: cnst.PRESENCE,
            cnst.TIME: time.time(),
            cnst.USER: {
                cnst.ACCOUNT_NAME: 'User',
                cnst.STATUS: 'online'
            },
            cnst.TYPE: cnst.STATUS
        }
        self.assertEqual(message, result)

    def test_handle_response_200(self):
        message = {
            cnst.RESPONSE: 200
        }
        result = '200 : OK'
        self.assertEqual(handle_response(message), result)

    def test_handle_response_400(self):
        message = {
            cnst.RESPONSE: 400,
            cnst.ERROR: 'bad request'
        }
        result = '400 : bad request'
        self.assertEqual(handle_response(message), result)

    def test_handle_response_402(self):
        message = {
            cnst.RESPONSE: 402,
            cnst.ERROR: 'no account with that name'
        }
        result = '402 : no account with that name'
        self.assertEqual(handle_response(message), result)

    def test_handle_response_error(self):
        message = {
        }
        self.assertRaises(ValueError, handle_response, message)


if __name__ == '__main__':
    unittest.main()
