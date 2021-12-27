import argparse
import inspect
import select
from socket import socket, AF_INET, SOCK_STREAM
from sqlite3 import IntegrityError

from constants import DEFAULT_IP, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, \
    USER, ACCOUNT_NAME, STATUS, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, ERROR, DEFAULT_PORT, \
    RESPONSE_200, RESPONSE_400, EXIT
from socket_include import Socket, SocketType, CheckServerPort
from socket_verifier import SocketVerifier
from server_database import ServerDB
from project_logging.config.log_config import server_logger as logger


def log(some_function):
    def wrapper(*args, **kwargs):
        logger.debug(
            f'Function: {some_function.__name__}, args: {args}, kwargs: {kwargs}, '
            f'called from function: {inspect.stack()[1][3]}'
        )
        result = some_function(*args, **kwargs)
        return result

    return wrapper


class ServerMeta(metaclass=SocketVerifier):
    pass


class Server(ServerMeta, Socket):
    socket_type = SocketType('Server')
    port = CheckServerPort()

    def __init__(self, server_ip, server_port, db):
        super().__init__()
        self.port = server_port
        self.host = server_ip
        self.socket = None
        self.clients = []
        self.client_usernames = {}
        self.messages = []
        self.database = db

    @log
    def handle_message(self, message, client_socket):
        """
        The function takes a message from the client and processes it.
        If message is presence-message, function returns a response message
        from the server
        If message is not presence function appends this message into messages_list

        :param message: received message: dict
        :param client_socket: client_socket

        """
        logger.info(
            f'{client_socket.getpeername()}: the message from the client is being handled'
        )
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            client_username = message[USER][ACCOUNT_NAME]
            client_ip, client_port = client_socket.getpeername()
            if client_username not in self.client_usernames.keys():
                logger.info(
                    f'{client_ip}:{client_port}: name \'{client_username}\' status \'{message[USER][STATUS]}\'')
                self.client_usernames[client_username] = client_socket
                logger.info(
                    f'{client_ip}:{client_port}: '
                    f'name \'{client_username}\' added into clients_usernames'
                )
                self.send_data(RESPONSE_200, client_socket)
                self.database.user_login(client_username, client_ip, client_port)
                logger.info(f'{client_username} login')

            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято'
                self.send_data(response, client_socket)
                self.clients.remove(client_socket)
                client_socket.close()

        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and \
                SENDER in message and DESTINATION in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            logger.info(f'message from: {message[SENDER]} to: {message[DESTINATION]} appended into messages_list')

        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            client_username = message[ACCOUNT_NAME]
            logger.info(f'{client_username} exit')
            self.database.user_logout(client_username)
            self.clients.remove(self.client_usernames[client_username])
            self.client_usernames[client_username].close()
            del self.client_usernames[client_username]

        else:
            self.send_data(RESPONSE_400, socket)
            logger.info(ERROR)

    @log
    def make_connection(self):
        """Создаёт сокет и устанавливает соединение"""
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(1)
        self.socket.listen(MAX_CONNECTIONS)

        if self.host != DEFAULT_IP:
            logger.info(f'server started at {self.port} and listened ip {self.host}')
        else:
            logger.info(f'server started at {self.port} and listened all ip')

    @log
    def accept_connection(self):
        """Принимает подключение от клиента"""
        try:
            client, client_address = self.socket.accept()
        except OSError:
            pass
        else:
            logger.info(
                f'{client.getpeername()}: client connection established')
            self.clients.append(client)

    @log
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
                    except IntegrityError:
                        logger.info(f'{client.getpeername()}: disconnected')
                        self.clients.remove(client)

            if self.messages and clients_receivers:
                data_to_send = self.messages.pop(0)
                for client in clients_receivers:
                    client_name = data_to_send[DESTINATION]
                    if client_name in self.client_usernames.keys() and \
                            client == self.client_usernames[client_name]:
                        try:
                            self.send_data(data_to_send, client)
                        except:
                            logger.info(f'{client.getpeername()}: connection lost')
                            self.clients.remove(client)
                            del self.client_usernames[client_name]


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключённых пользователей')
    print('history - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default=DEFAULT_IP, nargs='?',
                        help=f'server ip-address, default - {DEFAULT_IP}')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'server port, default - {DEFAULT_PORT}')

    cmd_args = parser.parse_args()
    ip_address = cmd_args.address
    port = cmd_args.port
    database = ServerDB()
    s = Server(ip_address, port, database)
    s.daemon = True
    s.start()

    print_help()

    while True:
        command = input('Введите команду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.get_all_users()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.get_active_users()):
                print(f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'history':
            name = input('Введите имя пользователя для просмотра истории. '
                         'Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()
