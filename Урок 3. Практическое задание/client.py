import json
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from common.constants import DEFAULT_IP, DEFAULT_PORT, ACTION, PRESENCE, TIME, \
    USER, ACCOUNT_NAME, TYPE, RESPONSE, ERROR, STATUS
from common.functions import send_message, get_message


def create_presence_message(user='Guest'):
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
    return output_message


def server_message_processing(message):
    """
    The function takes a message received from the server,
    processes it and
    returns a string with the server response code and its description
    :param message: message from server: dict
    :return: server answer: str
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return f'{message[RESPONSE]} : OK'
        return f'{message[RESPONSE]} : {message[ERROR]}'
    raise ValueError


def main():
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
            ip = DEFAULT_IP
    except IndexError:
        print('missing ip address')
        sys.exit(1)
    try:
        if '-u' in sys.argv:
            u = sys.argv.index('-u') + 1
            user = sys.argv[u]
        else:
            user = 'Guest'
    except IndexError:
        print('missing user')
        sys.exit(1)

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((ip, port))
    client_message = create_presence_message(user)
    send_message(sock, client_message)
    try:
        answer = server_message_processing(get_message(sock))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('the message from server is incorrect')


if __name__ == '__main__':
    main()
