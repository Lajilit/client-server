import json

from constants import DEFAULT_IP, DEFAULT_PORT, ENCODING, MAX_PACKAGE_LENGTH


class Socket:

    def __init__(self, host=DEFAULT_IP, port=DEFAULT_PORT):
        self.socket = None
        self.host = host
        self.port = port

    @staticmethod
    def send_data(message, socket_to_send=None):
        json_message = json.dumps(message)
        encoded_message = json_message.encode(ENCODING)
        socket_to_send.send(encoded_message)

    @staticmethod
    def receive_data(socket_to_receive=None):
        encoded_message = socket_to_receive.recv(MAX_PACKAGE_LENGTH)
        if isinstance(encoded_message, bytes):
            decoded_message = encoded_message.decode(ENCODING)
            message = json.loads(decoded_message)
            if isinstance(message, dict):
                return message
            raise ValueError
        raise ValueError

    def set_up(self):
        raise NotImplementedError
