import inspect
import json
import logging
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM
from constants import DEFAULT_PORT, ACTION, PRESENCE, TIME, \
    USER, ACCOUNT_NAME, TYPE, RESPONSE, ERROR, STATUS, DEFAULT_IP
from functions import send_message, get_message
import project_logging.config.client_log_config

client_logger = logging.getLogger('client')

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
    client_logger.debug(f'{user}: {PRESENCE} message is created')
    return output_message

@Log()
def handle_response(message):
    """
    The function takes a message received from the server,
    processes it and
    returns a string with the server response code and its description
    :param message: message from server: dict
    :return: server answer: str
    """
    client_logger.debug('the responce from the server is being handled')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return f'{message[RESPONSE]} : OK'
        return f'{message[RESPONSE]} : {message[ERROR]}'
    raise ValueError


def main():
    """
    The main function.
    The function receives from the command line parameters the ip
    address and port for connecting to the server and the username
    (if there are no port and user parameters, it uses the default
    values), generates a socket for the client and sends a presence
    message to the server. Waits for a response message from the server,
    processes it and displays the response.
    """
    # Help
    help_string = """parameters: client.py <addr> [<port>] [-u <user>]:
    addr - server ip-address (example 127.0.0.1)
    port - server port (default 7777)
    -u <user> - user name (default Guest)"""

    if 'help' in sys.argv or '-h' in sys.argv:
        print(help_string)
        sys.exit(1)

    parameters = ['-u']

    try:
        if sys.argv[1] not in parameters:
            addr = sys.argv[1]
        else:
            raise IndexError
    except IndexError:
        client_logger.warning('missing ip address: default ip used')
        addr = DEFAULT_IP

    try:
        if sys.argv[2] not in parameters:
            port = int(sys.argv[2])
            if port <= 1024 or port >= 65535:
                raise ValueError
        else:
            raise IndexError
    except IndexError:  # if not second parameter - use default value
        client_logger.warning('missing port number: default port used')
        port = DEFAULT_PORT

    except ValueError:
        client_logger.critical(f'wrong port number: {sys.argv[2]}')
        sys.exit(1)

    try:
        if '-u' in sys.argv:
            u = sys.argv.index('-u') + 1
            user = sys.argv[u]
        else:
            user = 'Guest'
    except IndexError:
        client_logger.critical('missing user')
        sys.exit(1)
    try:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((addr, port))
        client_logger.debug('trying to connect to server at '
                           f'{addr}:{port}')
    except ConnectionRefusedError:
        client_logger.critical('No connection could be made because the '
                                'target machine actively refused it')
        sys.exit(1)
    client_message = create_presence_message(user=user)
    send_message(sock, client_message)
    client_logger.debug('presense message was sent to the server')
    try:
        answer = handle_response(get_message(sock))
        client_logger.info(
            f'server response: {answer}'
        )
    except (ValueError, json.JSONDecodeError):
        client_logger.error(
            'the message from server is incorrect'
        )


if __name__ == '__main__':
    main()
