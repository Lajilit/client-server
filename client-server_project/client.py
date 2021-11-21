import argparse
import inspect
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from constants import ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, STATUS, TYPE, RESPONSE, ERROR, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, EXIT
from meta import SocketVerifier
from project_logging.config.log_config import client_logger
from socket_include import Socket


class ClientMeta(metaclass=SocketVerifier):
    pass


class Client(ClientMeta, Socket):

    def __init__(self, username):
        self.name = username
        super().__init__()

    @staticmethod
    def log(some_function):
        def wrapper(*args, **kwargs):
            client_logger.debug(
                f'Function: {some_function.__name__}, args: {args}, kwargs: {kwargs}, '
                f'called from function: {inspect.stack()[1][3]}'
            )
            result = some_function(*args, **kwargs)
            return result

        return wrapper

    @log
    def create_presence(self):
        output_message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.name,
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        client_logger.info(f'{self.name}: {PRESENCE} message is created')
        return output_message

    @log
    def handle_response(self, message):
        client_logger.info(
            f'{self.name}: the response from the server is being handled'
        )
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return f'OK'
            return f'{message[ERROR]}'

        return f'{self.name}: the response from server is incorrect'

    @log
    def create_message(self):

        input_destination = input(
            'Message recipient: '
        )
        input_message = input(
            'Enter your message text or press enter to shutdown: ')

        message = {
            ACTION: MESSAGE,
            TIME: time.time(),
            SENDER: self.name,
            DESTINATION: input_destination,
            MESSAGE_TEXT: input_message
        }
        client_logger.debug(
            f'{self.name}: message is created: {message}'
        )
        try:
            self.send_data(message, self.socket)
            client_logger.debug(
                f'{self.name}: message was sent to user {input_destination}'
            )
        except ConnectionRefusedError:
            client_logger.critical(
                f'{self.name}: server connection lost'
            )
            sys.exit(1)

    @log
    def listen_server(self):
        while True:
            try:
                message = self.receive_data(self.socket)
                client_logger.debug(
                    f'{self.name}: the message {message} is being handled'
                )
                if ACTION in message and \
                        message[ACTION] == MESSAGE and \
                        SENDER in message and \
                        MESSAGE_TEXT in message and \
                        DESTINATION in message:
                    client_logger.debug(
                        f'{self.name}: Received a message from the user '
                        f'{message[SENDER]}: {message[MESSAGE_TEXT]}'
                    )
                    print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
                else:
                    client_logger.info(
                        f'{self.name}: the message from server is incorrect:'
                        f' {message}')
            except ConnectionRefusedError:
                client_logger.critical(
                    f'{self.name}: server connection lost'
                )
                break

    @log
    def create_exit_message(self):
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.name
        }
        client_logger.info(
            f'{self.name}: {EXIT} message is created'
        )
        try:
            self.send_data(message, self.socket)
            client_logger.info(
                f'{self.name}: {EXIT} message was sent to the server'
            )
        except ConnectionRefusedError:
            client_logger.critical(
                f'{self.name}: server connection lost'
            )
            sys.exit(1)
        print('Connection closed')
        client_logger.info(f'{self.name}: connection closed')

    @staticmethod
    def help_function():
        print('Commands used:')
        print('message - command to send message')
        print('exit - command to exit')

    @log
    def user_interaction(self):
        self.help_function()

        while True:
            command = input('Enter command [message, exit]: ')
            if command == 'message':
                self.create_message()
            elif command == 'exit':
                self.create_exit_message()
                time.sleep(0.5)
                break
            else:
                self.help_function()

    def set_up(self):
        # Запуск клиента
        print('Client module')
        client_logger.info(
            f'Client module started'
        )

        # Подключение к серверу и отправка сообщения от присутствии
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            client_logger.info(
                f'{self.name}: trying to connect to server at '
                f'{self.host}:{self.port}'
            )
            self.send_data(self.create_presence(), self.socket)
            client_logger.info(
                f'{self.name}: presence message was sent to the server'
            )
            answer = self.handle_response(self.receive_data(self.socket))
            client_logger.debug(
                f'{self.name}: server response: {answer}'
            )
        except ConnectionRefusedError:
            client_logger.critical(
                f'{self.name}: no connection could be made because '
                f'the target machine actively refused it')
            sys.exit(1)
        # Работа с пользователем

        receiver = threading.Thread(target=self.listen_server)
        receiver.daemon = True
        receiver.start()
        client_logger.info(f'{self.name}: receiver process started')

        interface = threading.Thread(target=self.user_interaction)
        interface.daemon = True
        interface.start()
        client_logger.info(f'{self.name}: interface process started')

        while True:
            time.sleep(1)
            if receiver.is_alive() and interface.is_alive():
                continue
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--name', default='Guest', nargs='?',
                        help='user name, default - Guest')
    name = parser.parse_args().name
    client = Client(name)

    client.set_up()
