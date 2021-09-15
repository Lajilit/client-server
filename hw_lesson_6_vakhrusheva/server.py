import inspect
import json
import logging
import sys
from socket import socket, AF_INET, SOCK_STREAM
from constants import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, \
    PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, STATUS
from functions import get_message, send_message
import project_logging.config.server_log_config

users_db = ['Guest', 'Гость']

server_logger = logging.getLogger('server')

def log(func):

    def wrapper(*args, **kwargs):
        server_logger.debug(
            f'Function: {func.__name__}, args: {args}, kwargs: {kwargs}, '
            f'called from function: {inspect.stack()[1][3]}'
        )
        result = func(*args, **kwargs)
        return result
    return wrapper

@log
def handle_message(message):
    """
    The function takes a message from the client,
    processes it and
    returns a response message from the server

    :param message: received message: dict
    :return: response message: dict
    """
    server_logger.debug('the message from the client is being handled')
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] in users_db:
        server_logger.info(f'{message[USER][ACCOUNT_NAME]}: {message[USER][STATUS]}')
        return {RESPONSE: 200}
    elif USER in message and message[USER][ACCOUNT_NAME] not in users_db:
        return {
            RESPONSE: 402,
            ERROR: 'no account with that name'
        }
    return {
        RESPONSE: 400,
        ERROR: 'bad request'
    }


def main():
    """
    The function receives the server ip address and port from the
    command line parameters (if these parameters are absent, it uses
    the default values), generates a socket for the server and waits
    for a message from clients. When a message is received, processes it
    and sends a response
    """

    try:
        if '-p' in sys.argv:
            p = sys.argv.index('-p') + 1
            port = int(sys.argv[p])
            if port <= 1024 or port >= 65535:
                raise ValueError
        else:
            port = DEFAULT_PORT
    except IndexError:
        server_logger.warning(
            f'missing port number: default port {DEFAULT_PORT} used'
        )
        sys.exit(1)
    except ValueError:
        server_logger.critical(f'wrong port number: {sys.argv[p]}')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            a = sys.argv.index('-a') + 1
            ip = sys.argv[a]
        else:
            ip = ''
    except IndexError:
        server_logger.warning(f'missing ip address')
        sys.exit(1)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(MAX_CONNECTIONS)
    if ip:
        server_logger.info(f'server started at {port} and listened ip {ip}')
    else:
        server_logger.info(f'server started at {port} and listened all ip')

    while True:
        client_socket, client_address = sock.accept()
        server_logger.info(f'client connected: {client_address}')
        try:
            client_message = get_message(client_socket)
            server_logger.debug(f'message reseived {client_message}')
            server_response = handle_message(client_message)
            server_logger.debug(
                f'a response to the client is generated: {server_response}')
            send_message(client_socket, server_response)
            server_logger.debug('responce was sent to the client')
            client_socket.close()
            server_logger.debug('client connection closed')
        except (ValueError, json.JSONDecodeError):
            server_logger.error('the message from client is incorrect')
            client_socket.close()


if __name__ == '__main__':
    main()
    handle_message('text')