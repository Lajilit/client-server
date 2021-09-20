import argparse
import inspect
import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM

from constants import DEFAULT_PORT, ACTION, PRESENCE, TIME, \
    USER, ACCOUNT_NAME, TYPE, RESPONSE, ERROR, STATUS, DEFAULT_IP, MESSAGE, \
    SENDER, MESSAGE_TEXT
from functions import send_message, get_message
from project_logging.config.client_log_config import client_logger


# import logging
# client_logger = logging.getLogger('client')

class Log():

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            client_logger.debug(
                f'Function: {func.__name__}, args: {args}, kwargs: {kwargs}, '
                f'called from function: {inspect.stack()[1][3]}'
            )
            result = func(*args, **kwargs)
            return result

        return wrapper


@Log()
def client_arg_parser():
    """
    The function receives and processes script launch parameters from
    the command line
    :return: server_address, server_port, user_name, client_mode
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('address', default=DEFAULT_IP, nargs='?',
                        help=f'server ip-address, default - {DEFAULT_IP}')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'server port, default - {DEFAULT_PORT}')
    parser.add_argument('-n', '--name', default='Guest', nargs='?',
                        help='user name, default - Guest')
    args = parser.parse_args()
    address = args.address
    port = args.port
    user_name = args.name

    if port <= 1024 or port >= 65535:
        client_logger.critical(f'wrong port number: {port}')
        sys.exit(1)

    return address, port, user_name


@Log()
def create_presence_message(user):
    """
    The function generates a presence message for the user
    :param user: user name: str
    :return: presence message: dict
    """
    output_message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: user,
            STATUS: 'online'
        },
        TYPE: STATUS
    }
    client_logger.debug(f'{user}: {PRESENCE} message is created')
    return output_message


@Log()
def handle_response(message):
    """
    The function takes a response from the server,
    processes it and
    returns a string with the server response code and its description
    :param message: message from server: dict
    :return: server answer: str
    """
    client_logger.debug(f'the response from the server is being handled')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return f'OK'
        return f'{message[ERROR]}'

    return 'the response from server is incorrect'

@Log()
def create_message(sock, user='Guest'):
    """
    The function asks for the user input message_text and generates a
    message for the user
    :param user: user name: str
    :return: presence message: dict
    """
    input_message = input(
        'Enter your message text or press enter to shutdown: ')
    if not input_message:
        sock.close()
        client_logger.info('user output')
        sys.exit(0)
    message = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: user,
        MESSAGE_TEXT: input_message
    }
    client_logger.debug(f'{user}: message is created: {message}')
    return message

@Log()
def handle_message(message):
    """
    The function takes a message, processes it and
    returns a string with the server response code and its description
    :param message: message from server: dict
    :return: server answer: str
    """
    client_logger.debug('the message {message} is being handled')
    if ACTION in message and \
            message[ACTION] == MESSAGE and \
            SENDER in message and \
            MESSAGE_TEXT in message:
        return f'Received a message from the user ' \
               f'{message[SENDER]}: {message[MESSAGE_TEXT]}'

    return 'the message from server is incorrect'


def main():
    """
    The main function.
    The function receives from the command line parameters the ip
    address and port for connecting to the server, the username and
    the server operation mode, (if these parameters are absent, it uses
    the default values) and generates a socket for the client.
    If 'client_mode' is 'send', client sends a message to the server.
    If 'client_mode' is 'listen, client wait for the message from server,
    receives, handle and displays it.
    """
    addr, port, user_name = client_arg_parser()
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((addr, port))
        client_logger.debug(
            f'{user_name}: trying to connect to server at {addr}:{port}'
        )
        presence_message = create_presence_message(user_name)
        send_message(sock, presence_message)
        client_logger.debug(
            f'{user_name}: presense message was sent to the server'
        )
        answer = handle_response(get_message(sock))
        client_logger.debug(
            f'{user_name}: server response: {answer}'
        )
    except ConnectionRefusedError:
        client_logger.critical('No connection could be made because the '
                               'target machine actively refused it')
        sys.exit(1)

    else:
        pass


if __name__ == '__main__':
    main()
