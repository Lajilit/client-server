import json
import sys
from enum import Enum
from constants import ENCODING, MAX_PACKAGE_LENGTH
from errors import IncorrectDataReceivedError, NonDictDataError


class SocketType(Enum):
    SERVER = 'Server'
    CLIENT = 'Client'


class CheckServerPort:

    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return int(f'{getattr(instance, self.name)}')

    def __set__(self, instance, value):
        try:
            value = int(value)
            if not (1024 <= value <= 65535):
                raise ValueError
        except ValueError:
            print('Номер порта должен быть целым числом в пределах от 1024 до 65535')
            sys.exit(1)
        else:
            setattr(instance, self.name, value)

    def __delete__(self, instance):
        raise AttributeError('Невозможно удалить атрибут')


class MySocket:

    def __init__(self):
        self.socket = None

    def send_data(self, message, socket_to_send=None):
        if not isinstance(message, dict):
            raise NonDictDataError
        json_message = json.dumps(message)
        encoded_message = json_message.encode(ENCODING)
        if not socket_to_send:
            socket_to_send = self.socket
        socket_to_send.send(encoded_message)

    def receive_data(self, socket_to_receive=None):
        if not socket_to_receive:
            socket_to_receive = self.socket
        encoded_message = socket_to_receive.recv(MAX_PACKAGE_LENGTH)
        if isinstance(encoded_message, bytes):
            decoded_message = encoded_message.decode(ENCODING)
            data = json.loads(decoded_message)
            if isinstance(data, dict):
                return data
            raise IncorrectDataReceivedError
        raise IncorrectDataReceivedError
