import json
import sys
from socket import socket, AF_INET, SOCK_STREAM

from common.constants import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, \
    PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, STATUS
from common.functions import get_message, send_message

users_db = ['Guest', 'Гость']


def handle_message(message):
    """
    The function takes a message from the client,
    processes it and
    returns a response message from the server

    :param message: received message: dict
    :return: response message: dict
    """
    if ACTION in message \
            and message[ACTION] == PRESENCE \
            and TIME in message \
            and USER in message \
            and message[USER][ACCOUNT_NAME] in users_db:
        print(f'{message[USER][ACCOUNT_NAME]}: {message[USER][STATUS]}')
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
        print('missing port number')
        sys.exit(1)
    except ValueError:
        print('wrong port number')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            a = sys.argv.index('-a') + 1
            ip = sys.argv[a]
        else:
            ip = ''
    except IndexError:
        print('missing ip address')
        sys.exit(1)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(MAX_CONNECTIONS)

    while True:
        client_socket, client_address = sock.accept()
        try:
            client_message = get_message(client_socket)
            print(client_message)
            server_response = handle_message(client_message)
            send_message(client_socket, server_response)
            client_socket.close()
        except (ValueError, json.JSONDecodeError):
            print('the message from client is incorrect')
            client_socket.close()


if __name__ == '__main__':
    main()
