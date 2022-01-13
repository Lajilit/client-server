import argparse
import select
import threading
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
from sqlite3 import IntegrityError
from json.decoder import JSONDecodeError

from constants import DEFAULT_IP, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, \
    USERNAME, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, ERROR, DEFAULT_PORT, \
    RESPONSE_200, RESPONSE_400, EXIT, ADD_CONTACT, REMOVE_CONTACT, GET_ALL_USERS, RESPONSE_202, LIST_INFO, \
    GET_CONTACTS, CONTACT_NAME, GET_ACTIVE_USERS
from errors import ServerError
from socket_include import MySocket, SocketType, CheckServerPort
from server_database import ServerDB
from project_logging.config.log_config import server_logger as logger


class Server(threading.Thread, MySocket):
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

    def make_connection(self):
        """Создаёт сокет и устанавливает соединение"""
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(1)
        self.socket.listen(MAX_CONNECTIONS)

        if self.host != DEFAULT_IP:
            logger.info(f'server started at {self.port} and listened ip {self.host}')
        else:
            logger.info(f'server started at {self.port} and listened all ip')

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
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USERNAME in message:
            client_username = message[USERNAME]
            client_ip, client_port = client_socket.getpeername()
            if client_username not in self.client_usernames.keys():
                logger.info(
                    f'{client_ip}:{client_port}: name \'{client_username}\'')
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
                response[ERROR] = 'Username already in use'
                self.send_data(response, client_socket)
                self.clients.remove(client_socket)
                client_socket.close()

        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and \
                SENDER in message and DESTINATION in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            self.database.database_handle_message(
                message[SENDER], message[DESTINATION])
            logger.info(
                f'message from: {message[SENDER]} to: {message[DESTINATION]} appended into messages_list')

        elif ACTION in message and message[ACTION] == EXIT and USERNAME in message:
            client_username = message[USERNAME]
            logger.info(f'{client_username} exit')
            self.database.user_logout(client_username)
            self.clients.remove(client_socket)
            client_socket.close()
            del self.client_usernames[client_username]

        elif ACTION in message and message[ACTION] == GET_CONTACTS and USERNAME in message:
            client_username = message[USERNAME]
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(client_username)
            self.send_data(response, client_socket)

        elif ACTION in message and message[ACTION] == GET_ALL_USERS and USERNAME in message:
            response = RESPONSE_202
            response[LIST_INFO] = [username for username, last_connection_time in self.database.get_all_users()]
            self.send_data(response, client_socket)

        elif ACTION in message and message[ACTION] == GET_ACTIVE_USERS and USERNAME in message:
            response = RESPONSE_202
            response[LIST_INFO] = [
                username for username, ip, port, last_connection_time in self.database.get_active_users()
            ]
            self.send_data(response, client_socket)

        elif ACTION in message and message[ACTION] == ADD_CONTACT and USERNAME in message and CONTACT_NAME in message:
            client_username = message[USERNAME]
            contact_username = message[CONTACT_NAME]
            try:
                self.database.add_contact(client_username, contact_username)
            except ServerError as e:
                response = RESPONSE_400
                response[ERROR] = f'{e.args}'
                self.send_data(response, client_socket)
                logger.info(e)
            else:
                logger.info(f'{client_username} add contact {contact_username}')
                self.send_data(RESPONSE_200, client_socket)

        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and USERNAME in message and CONTACT_NAME in message:
            client_username = message[USERNAME]
            contact_username = message[CONTACT_NAME]
            logger.info(f'{client_username} removed contact {contact_username}')
            self.database.remove_contact(client_username, contact_username)
            self.send_data(RESPONSE_200, client_socket)

        else:
            self.send_data(RESPONSE_400, client_socket)
            logger.info(ERROR)

    def client_logout(self, client):
        for username in self.client_usernames:
            if self.client_usernames[username] == client:
                self.database.user_logout(username)
                del self.client_usernames[username]
                break
        self.clients.remove(client)

    def run(self):
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
            except OSError as e:
                logger.error(f'Socket error: {e.args}')

            if clients_senders:
                for client in clients_senders:
                    try:
                        received_message = self.receive_data(client)
                        self.handle_message(received_message, client)
                    except IntegrityError as e:
                        logger.info(f'{client.getpeername()}: disconnected {e.args}')
                        self.client_logout(client)
                    except OSError as e:
                        logger.info(f'{client.getpeername()}: disconnected {e.args}')
                        self.client_logout(client)
                    except JSONDecodeError as e:
                        logger.info(f'{client.getpeername()}: connection lost {e.args}')
                        self.client_logout(client)

            if self.messages and clients_receivers:
                data_to_send = self.messages.pop(0)
                client_name = data_to_send[DESTINATION]
                for client in clients_receivers:
                    if client_name in self.client_usernames.keys() and \
                            client == self.client_usernames[client_name]:
                        try:
                            self.send_data(data_to_send, client)
                        except Exception as e:
                            logger.info(f'{client.getpeername()}: connection lost: {e.args}')
                            self.client_logout(client)


def print_help():
    print('Поддерживаемые команды:')
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
