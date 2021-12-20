import argparse
import inspect
import time
import select
from socket import socket, AF_INET, SOCK_STREAM

from constants import DEFAULT_IP, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, \
    USER, ACCOUNT_NAME, STATUS, RESPONSE, ALERT, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, ERROR, DEFAULT_PORT
from socket_include import Socket, SocketType, CheckServerPort
from project_logging.config.log_config import server_logger


class Server(Socket):
    socket_type = SocketType('Server')
    port = CheckServerPort()

    def __init__(self, server_ip, server_port):
        super().__init__()
        self.port = server_port
        self.host = server_ip
        self.socket = None
        self.clients = []
        self.client_usernames = {}
        self.messages = []

    @staticmethod
    def log(some_function):
        def wrapper(*args, **kwargs):
            server_logger.debug(
                f'Function: {some_function.__name__}, args: {args}, kwargs: {kwargs}, '
                f'called from function: {inspect.stack()[1][3]}'
            )
            result = some_function(*args, **kwargs)
            return result
        return wrapper

    # @log
    def handle_message(self, message, client_socket):
        """
        The function takes a message from the client and processes it.
        If message is presence-message, function returns a response message
        from the server
        If message is not presence function appends this message into messages_list

        :param message: received message: dict
        :param client_socket: client_socket

        """
        server_logger.info(
            f'{client_socket.getpeername()}: the message from the client is being handled'
        )
        if ACTION in message \
                and message[ACTION] == PRESENCE \
                and TIME in message \
                and USER in message:
            server_logger.info(
                f'{client_socket.getpeername()}: '
                f'name \'{message[USER][ACCOUNT_NAME]}\' '
                f'status \'{message[USER][STATUS]}\'')
            response = {
                RESPONSE: 200,
                ALERT: 'ok'
            }
            self.send_data(response, client_socket)
            self.client_usernames[message[USER][ACCOUNT_NAME]] = client_socket
            server_logger.info(
                f'{client_socket.getpeername()}: '
                f'name \'{message[USER][ACCOUNT_NAME]}\' added into clients_usernames'
            )
        elif ACTION in message and \
                message[ACTION] == MESSAGE and \
                TIME in message and \
                SENDER in message and \
                DESTINATION in message and \
                MESSAGE_TEXT in message:
            self.messages.append((
                message[SENDER],
                message[DESTINATION],
                message[MESSAGE_TEXT],
            ))
            server_logger.info(f'message: {message[MESSAGE_TEXT]} '
                               f'from: {message[SENDER]} '
                               f'to: {message[DESTINATION]} '
                               f'appended into messages_list')

        else:
            response = {
                RESPONSE: 400,
                ERROR: 'Bad Request'
            }
            self.send_data(response, socket)
            server_logger.info(ERROR)

    # @log
    def make_connection(self):
        """Создаёт сокет и устанавливает соединение"""
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(1)
        self.socket.listen(MAX_CONNECTIONS)

        if self.host != DEFAULT_IP:
            server_logger.info(f'server started at {self.port} and listened ip {self.host}')
        else:
            server_logger.info(f'server started at {self.port} and listened all ip')

    # @log
    def accept_connection(self):
        """Принимает подключение от клиента"""
        try:
            client, client_address = self.socket.accept()
        except OSError:
            pass
        else:
            server_logger.info(
                f'{client.getpeername()}: client connection established')
            self.clients.append(client)

    # @log
    def start(self):
        self.make_connection()

        while True:
            self.accept_connection()
            clients_senders = []
            clients_receivers = []
            try:
                if self.clients:
                    clients_senders, clients_receivers, e = select.select(
                        self.clients, self.clients, [], 0
                    )
            except OSError:
                pass

            if clients_senders:
                for client in clients_senders:
                    try:
                        received_message = self.receive_data(client)
                        self.handle_message(received_message, client)
                    except Exception:
                        server_logger.info(
                            f'{client.getpeername()}: client disconnected'
                        )
                        self.clients.remove(client)

            if self.messages and clients_receivers:
                data = self.messages.pop(0)
                data_to_send = {
                    ACTION: MESSAGE,
                    TIME: time.time(),
                    SENDER: data[0],
                    DESTINATION: data[1],
                    MESSAGE_TEXT: data[2]
                }

                for client in clients_receivers:
                    client_name = data_to_send[DESTINATION]
                    if client_name in self.client_usernames.keys() and \
                            client == self.client_usernames[client_name]:
                        try:
                            self.send_data(data_to_send, client)
                        except Exception:
                            server_logger.info(
                                f'{client.getpeername()}: client disconnected'
                            )
                            self.clients.remove(client)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default=DEFAULT_IP, nargs='?',
                        help=f'server ip-address, default - {DEFAULT_IP}')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'server port, default - {DEFAULT_PORT}')

    cmd_args = parser.parse_args()
    ip_address = cmd_args.address
    port = cmd_args.port
    s = Server(ip_address, port)
    s.start()
