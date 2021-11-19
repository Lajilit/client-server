import argparse
import inspect
import select
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM

from constants import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, \
    PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, STATUS, MESSAGE, \
    MESSAGE_TEXT, SENDER, ALERT, DESTINATION
from functions import get_message, send_message
from project_logging.config.server_log_config import server_logger


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
def server_arg_parser():
    """
    The function receives and processes script launch parameters from
    the command line
    :return: ip address, port
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', default='', nargs='?',
                        help=f'ip address for connecting to the server, '
                             f'default - listened all ip ')
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'port for connecting to the server, '
                             f'default - {DEFAULT_PORT}')
    args = parser.parse_args()
    address = args.a
    port = args.p

    if port <= 1024 or port >= 65535:
        server_logger.critical(f'wrong port number: {port}')
        sys.exit(1)

    return address, port


@log
def handle_message(message, messages_list, socket):
    """
    The function takes a message from the client and processes it.
    If message is presense-message, function returns a response message
    from the server
    If message is not precense function appends this message into messages_list

    :param message: received message: dict
    :param messages_list: list
    :param socket: client socket

    """
    server_logger.info(
        f'{socket.getpeername()}: the message from the client is being handled'
    )
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message:
        server_logger.info(
            f'{socket.getpeername()}: '
            f'name \'{message[USER][ACCOUNT_NAME]}\' '
            f'status \'{message[USER][STATUS]}\'')
        send_message(socket, {
            RESPONSE: 200,
            ALERT: 'ok'
        })
        users[message[USER][ACCOUNT_NAME]] = socket
        server_logger.info(
            f'{socket.getpeername()}: '
            f'name \'{message[USER][ACCOUNT_NAME]}\' added into users_dict'
        )
    elif ACTION in message and \
            message[ACTION] == MESSAGE and \
            TIME in message and \
            SENDER in message and \
            DESTINATION in message and \
            MESSAGE_TEXT in message:
        messages_list.append((
            message[SENDER],
            message[DESTINATION],
            message[MESSAGE_TEXT],
        ))
        server_logger.info(f'message: {message[MESSAGE_TEXT]} '
                           f'from: {message[SENDER]} '
                           f'to: {message[DESTINATION]} '
                           f'appended into messages_list')

    else:
        send_message(socket, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        server_logger.info(ERROR)


def main():
    """
    The function receives the server ip address and port from the
    command line parameters (if these parameters are absent, it uses
    the default values), generates a socket for the server, waits
    for messages from clients and handle it. If message action is
    'presense', server sends a response. If message action is 'message',
     server sends message to other clients.
    """
    ip, port = server_arg_parser()

    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((ip, port))
    sock.settimeout(1)
    sock.listen(MAX_CONNECTIONS)

    if ip:
        server_logger.info(f'server started at {port} and listened ip {ip}')
    else:
        server_logger.info(f'server started at {port} and listened all ip')

    all_clients = []
    messages_list = []
    global users
    users = {}

    while True:

        try:
            client, client_address = sock.accept()
        except OSError:
            pass
        else:
            server_logger.info(
                f'{client.getpeername()}: client connection established')
            all_clients.append(client)
        clients_senders = []
        clients_receivers = []

        try:
            if all_clients:
                clients_senders, clients_receivers, e = select.select(
                    all_clients, all_clients, [], 0
                )
        except OSError:
            pass
        if clients_senders:
            for client in clients_senders:
                try:
                    received_message = get_message(client)
                    handle_message(received_message, messages_list, client)
                except:
                    server_logger.info(
                        f'{client.getpeername()}: client disconnected'
                    )
                    all_clients.remove(client)

        if messages_list and clients_receivers:
            message_in_list = messages_list.pop(0)
            message_to_send = {
                ACTION: MESSAGE,
                TIME: time.time(),
                SENDER: message_in_list[0],
                DESTINATION: message_in_list[1],
                MESSAGE_TEXT: message_in_list[2]
            }

            for client in clients_receivers:
                if client == users[message_to_send[DESTINATION]]:
                    try:
                        send_message(client, message_to_send)
                    except Exception:
                        server_logger.info(
                            f'{client.getpeername()}: client disconnected'
                        )
                        all_clients.remove(client)


if __name__ == '__main__':
    main()
