import argparse
import inspect
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from constants import DEFAULT_PORT, ACTION, PRESENCE, TIME, \
    USER, ACCOUNT_NAME, TYPE, RESPONSE, ERROR, STATUS, DEFAULT_IP, MESSAGE, \
    SENDER, MESSAGE_TEXT, DESTINATION, EXIT
from functions import send_message, get_message
from project_logging.config.client_log_config import client_logger


class Log:

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
def presence_message(user_name):
    """
    The function generates a presence message for the user
    :param user_name: user name: str
    :return: presence message: dict
    """
    output_message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: user_name,
            STATUS: 'online'
        },
        TYPE: STATUS
    }
    client_logger.info(f'{user_name}: {PRESENCE} message is created')
    return output_message


@Log()
def handle_response(message, user_name):
    """
    The function takes a response from the server,
    processes it and
    returns a string with the server response code and its description
    :param user_name:
    :param message: message from server: dict
    :return: server answer: str
    """
    client_logger.info(
        f'{user_name}: the response from the server is being handled'
    )
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return f'OK'
        return f'{message[ERROR]}'

    return f'{user_name}: the response from server is incorrect'


@Log()
def help_function():
    print('Commands used:')
    print('message - command to send message')
    print('exit - command to exit')


@Log()
def user_interaction(socket, user_name):
    help_function()

    while True:
        command = input('Enter command [message, exit]: ')
        if command == 'message':
            create_message(socket, user_name)
        elif command == 'exit':
            create_exit_message(socket, user_name)
            time.sleep(0.5)
            break
        else:
            help_function()


@Log()
def create_message(socket, user_name):
    """
    The function asks for the user input message_text and generates a
    message for the user
    :param socket:
    :param user_name: user name: str
    :return: presence message: dict
    """
    input_destination = input(
        'Message recipient: '
    )
    input_message = input(
        'Enter your message text or press enter to shutdown: ')

    message = {
        ACTION: MESSAGE,
        TIME: time.time(),
        SENDER: user_name,
        DESTINATION: input_destination,
        MESSAGE_TEXT: input_message
    }
    client_logger.info(
        f'{user_name}: message is created: {message}'
    )
    try:
        send_message(socket, message)
        client_logger.info(
            f'{user_name}: message was sent to user {input_destination}'
        )
    except ConnectionRefusedError:
        client_logger.critical(
            f'{user_name}: server connection lost'
        )
        sys.exit(1)


@Log()
def handle_message(socket, user_name):
    """
    The function takes a server socket and user name, processes it and
    returns a string with the server response code and its description
    :param user_name:
    :param socket: server socket
    :return: server answer: str
    """
    while True:
        try:
            message = get_message(socket)
            client_logger.info(
                f'{user_name}: the message {message} is being handled'
            )
            if ACTION in message and \
                    message[ACTION] == MESSAGE and \
                    SENDER in message and \
                    MESSAGE_TEXT in message and \
                    DESTINATION in message:
                client_logger.debug(
                    f'{user_name}: Received a message from the user '
                    f'{message[SENDER]}: {message[MESSAGE_TEXT]}'
                )
                print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
            else:
                client_logger.info(
                    f'{user_name}: the message from server is incorrect:'
                    f' {message}')
        except ConnectionRefusedError:
            client_logger.critical(
                f'{user_name}: server connection lost'
            )
            break


@Log()
def create_exit_message(socket, user_name):
    message = {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: user_name
    }
    client_logger.info(
        f'{user_name}: {EXIT} message is created'
    )
    try:
        send_message(socket, message)
        client_logger.info(
            f'{user_name}: {EXIT} message was sent to the server'
        )
    except ConnectionRefusedError:
        client_logger.critical(
            f'{user_name}: server connection lost'
        )
        sys.exit(1)
    print('Connection closed')
    client_logger.info(f'{user_name}: connection closed')


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
    # Запуск клиента
    print('Client module')
    client_logger.info(
        f'Client module started'
    )
    # Получение аргументов командной строки
    server_ip, server_port, username = client_arg_parser()

    # Подключение к серверу и отправка сообщения от присутствии
    try:
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.connect((server_ip, server_port))
        client_logger.info(
            f'{username}: trying to connect to server at '
            f'{server_ip}:{server_port}'
        )
        send_message(server_socket, presence_message(username))
        client_logger.info(
            f'{username}: presence message was sent to the server'
        )
        answer = handle_response(get_message(server_socket), username)
        client_logger.info(
            f'{username}: server response: {answer}'
        )
    except ConnectionRefusedError:
        client_logger.critical(
            f'{username}: no connection could be made because '
            f'the target machine actively refused it')
        sys.exit(1)
    # Работа с пользователем

    receiver = threading.Thread(target=handle_message,
                                args=(server_socket, username))
    receiver.daemon = True
    receiver.start()
    client_logger.info(f'{username}: receiver process started')

    interface = threading.Thread(target=user_interaction,
                                 args=(server_socket, username))
    interface.daemon = True
    interface.start()
    client_logger.info(f'{username}: interface process started')

    while True:
        time.sleep(1)
        if receiver.is_alive() and interface.is_alive():
            continue
        break


if __name__ == '__main__':
    main()
