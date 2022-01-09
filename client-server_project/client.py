import argparse
import inspect
import json
import socket
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from constants import DEFAULT_IP, DEFAULT_PORT,  ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, STATUS, TYPE, RESPONSE, ERROR, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, EXIT
from project_logging.config.log_config import client_logger as logger
from socket_verifier import SocketVerifier
from socket_include import Socket, SocketType
from errors import RequiredFieldMissedError, ServerError, IncorrectDataReceivedError

socket_lock = threading.Lock()
database_lock = threading.Lock()


def log(some_function):
    def wrapper(*args, **kwargs):
        logger.debug(
            f'Function: {some_function.__name__}, args: {args}, kwargs: {kwargs}, '
            f'called from function: {inspect.stack()[1][3]}'
        )
        result = some_function(*args, **kwargs)
        return result

    return wrapper


class ClientMeta(metaclass=SocketVerifier):
    pass


class Client(ClientMeta, Socket):
    socket_type = SocketType('Client')

    def __init__(self, name, server_ip_address, server_port):
        super().__init__()
        self.name = name
        self.port = server_port
        self.host = server_ip_address

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
        logger.info(f'{self.name}: {PRESENCE} message is created')
        return output_message

    @log
    def handle_response(self, message):
        logger.info(
            f'{self.name}: the response from the server is being handled'
        )
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return f'OK'
            return f'{message[ERROR]}'
        raise RequiredFieldMissedError(RESPONSE)

    @staticmethod
    def help_function():
        print('Commands used:')
        print('message - command to send message')
        print('exit - command to exit')

    @log
    def create_message(self):

        destination = input(
            'Message recipient: '
        )
        message_text = input(
            'Enter your message text or press enter to shutdown: ')

        message = {
            ACTION: MESSAGE,
            TIME: time.time(),
            SENDER: self.name,
            DESTINATION: destination,
            MESSAGE_TEXT: message_text
        }
        logger.debug(
            f'{self.name}: message is created: {message}'
        )
        return message, destination

    @log
    def create_exit_message(self):
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.name
        }
        logger.info(
            f'{self.name}: {EXIT} message is created'
        )
        return message

    @log
    def user_interaction(self):
        self.help_function()

        while True:
            command = input('Enter command [message, exit]: ')
            if command == 'message':
                message, destination = self.create_message()
                try:
                    self.send_data(message, self.socket)
                    logger.debug(
                        f'{self.name}: message was sent to user {destination}'
                    )
                except ConnectionRefusedError:
                    logger.critical(
                        f'{self.name}: server connection lost'
                    )
                    sys.exit(1)

            elif command == 'exit':
                message = self.create_exit_message()
                try:
                    self.send_data(message, self.socket)
                    logger.info(
                        f'{self.name}: {EXIT} message was sent to the server'
                    )
                except ConnectionRefusedError:
                    logger.critical(
                        f'{self.name}: server connection lost'
                    )
                    sys.exit(1)
                print('Connection closed')
                logger.info(f'{self.name}: connection closed')
                time.sleep(0.5)
                break
            else:
                self.help_function()

    @log
    def listen_server(self):
        while True:
            try:
                message = self.receive_data(self.socket)
            except IncorrectDataReceivedError as e:
                logger.debug(e)
            except OSError as e:
                if e.errno:
                    logger.critical(f'{self.name}: server connection lost')
                    break
            except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.decoder.JSONDecodeError):
                logger.critical(f'{self.name}: server connection lost')
                break
            else:
                logger.debug(f'{self.name}: the message {message} is being handled')
                if ACTION in message and \
                        message[ACTION] == MESSAGE and \
                        SENDER in message and \
                        MESSAGE_TEXT in message and \
                        DESTINATION in message:
                    logger.debug(
                        f'{self.name}: Received a message from the user '
                        f'{message[SENDER]}: {message[MESSAGE_TEXT]}'
                    )
                    print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
                else:
                    logger.info(
                        f'{self.name}: the message from server is incorrect:'
                        f' {message}')

    def start(self):
        # Запуск клиента
        print('Client module')
        logger.info(
            f'Client module started'
        )

        # Подключение к серверу и отправка сообщения от присутствии
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(
                f'{self.name}: trying to connect to server at '
                f'{self.host}:{self.port}'
            )
            self.send_data(self.create_presence(), self.socket)
            logger.info(
                f'{self.name}: presence message was sent to the server'
            )
            answer = self.handle_response(self.receive_data(self.socket))
            logger.debug(
                f'{self.name}: server response: {answer}'
            )
        except json.decoder.JSONDecodeError:
            logger.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as e:
            logger.error(f'При установке соединения сервер вернул ошибку: {e.error_text}')
            sys.exit(1)
        except RequiredFieldMissedError as e:
            logger.error(f'В ответе сервера отсутствует необходимое поле {e.missed_field}')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            logger.critical(
                f'{self.host}:{self.port}: no connection could be made because the target machine actively refused it')
            sys.exit(1)
        # Работа с пользователем

        receiver = threading.Thread(target=self.listen_server)
        receiver.daemon = True
        receiver.start()
        logger.info(f'{self.name}: receiver process started')

        interface = threading.Thread(target=self.user_interaction)
        interface.daemon = True
        interface.start()
        logger.info(f'{self.name}: interface process started')

        while True:
            time.sleep(1)
            if receiver.is_alive() and interface.is_alive():
                continue
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default=DEFAULT_IP, nargs='?',
                        help=f'server ip-address, default - {DEFAULT_IP}')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'server port, default - {DEFAULT_PORT}')
    parser.add_argument('-n', '--name', default='Guest', nargs='?',
                        help='user name, default - Guest')
    cmd_args = parser.parse_args()
    ip_address = cmd_args.address
    port = cmd_args.port
    username = cmd_args.name

    client = Client(username, ip_address, port)
    client.start()
