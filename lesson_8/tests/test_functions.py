import json
import unittest
import os, sys

parent_directory = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_directory)

from constants import ENCODING
from functions import send_message, get_message


class TestSocket:
    def __init__(self, bytes_string=None):
        self.message_in_socket = bytes_string
        self.message_to_socket = None
        self.max_package_length = None

    def send(self, message):
        self.message_to_socket = message

    def recv(self, max_package_length):
        self.max_package_length = max_package_length
        return self.message_in_socket


class TestFunctions(unittest.TestCase):
    test_dict = {
        'action': 'presence',
        'time': 00.0000,
        'user': {
            'account_name': 'user',
            'status': 'online'
        }
    }

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_send_message(self):
        message = self.test_dict
        test_socket = TestSocket()
        example_message = json.dumps(message).encode(ENCODING)
        send_message(test_socket, message)
        checked_message = test_socket.message_to_socket

        self.assertEqual(example_message, checked_message)

    def test_get_message_ok(self):
        message = b'{"action": "presence", "time": 0.0, "user": "user"}'
        test_socket = TestSocket(message)
        example_message = json.loads(message.decode(ENCODING))

        self.assertEqual(get_message(test_socket), example_message)

    def test_get_message_not_dict(self):
        message = b'it is not a dict'
        test_socket = TestSocket(message)
        with self.assertRaises(Exception):
            get_message(test_socket)

    def test_get_message_not_bytes_string(self):
        message = 'it is not a bytes string'
        test_socket = TestSocket(message)
        with self.assertRaises(Exception):
            get_message(test_socket)


if __name__ == '__main__':
    unittest.main()
