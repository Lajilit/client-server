import argparse
import configparser
import os
import select
import sys
import threading
from json.decoder import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
from sqlite3 import IntegrityError

from PyQt5.QtWidgets import QApplication

from common.constants import DEFAULT_IP, MAX_CONNECTIONS, ACTION, PRESENCE, TIME, \
    ACCOUNT_NAME, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, ERROR, RESPONSE_200, RESPONSE_400, EXIT, ADD_CONTACT, \
    REMOVE_CONTACT, GET_ALL_USERS, RESPONSE_202, LIST_INFO, \
    GET_CONTACTS, CONTACT_NAME, GET_ACTIVE_USERS, RESPONSE_404, DEFAULT_PORT, LISTEN_ADDRESS
from common.errors import ServerError
from project_logging.log_config import server_logger as logger
from server.server_database import ServerDB
from server.server_main_window import ServerMainWindow
from common.socket_include import MySocket, SocketType, CheckServerPort

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

new_connection = False
conflag_lock = threading.Lock()


class Server(threading.Thread, MySocket):
    socket_type = SocketType('Server')
    port = CheckServerPort()

    def __init__(self, server_ip, server_port, db):
        super().__init__()
        self.port = server_port
        self.host = server_ip
        self.database = db
        self.socket = None
        self.clients = []
        self.client_usernames = {}
        self.messages = []

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

    def handle_request(self, request, client_socket):
        """
        The function takes a message from the client and processes it.
        If message is presence-message, function returns a response message
        from the server
        If message is not presence function appends this message into messages_list

        :param request: received message: dict
        :param client_socket: client_socket

        """
        global new_connection
        logger.info(
            f'{client_socket.getpeername()}: the request from the client is being handled'
        )
        if ACTION in request and request[ACTION] == PRESENCE and TIME in request and ACCOUNT_NAME in request:
            client_username = request[ACCOUNT_NAME]
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
                with conflag_lock:
                    new_connection = True
            else:
                request = RESPONSE_400
                request[ERROR] = 'Username already in use'
                self.send_data(request, client_socket)
                self.clients.remove(client_socket)
                client_socket.close()

        elif ACTION in request and request[ACTION] == MESSAGE and TIME in request and \
                SENDER in request and DESTINATION in request and MESSAGE_TEXT in request:
            if request[DESTINATION] in self.client_usernames.keys():
                response = RESPONSE_200
                self.messages.append(request)
                self.database.database_handle_message(
                    request[SENDER], request[DESTINATION])
                logger.info(f'message from: {request[SENDER]} to: {request[DESTINATION]} appended into messages_list')
            else:
                response = RESPONSE_404
                response[ERROR] = f'user {request[DESTINATION]} is not registered on the server'
                logger.info(f'{request[SENDER]}: {response[ERROR]}')
            self.send_data(response, client_socket)

        elif ACTION in request and request[ACTION] == EXIT and ACCOUNT_NAME in request:
            client_username = request[ACCOUNT_NAME]
            logger.info(f'{client_username} exit')
            del self.client_usernames[client_username]
            self.database.user_logout(client_username)
            self.clients.remove(client_socket)
            client_socket.close()
            with conflag_lock:
                new_connection = True

        elif ACTION in request and request[ACTION] == GET_CONTACTS and ACCOUNT_NAME in request:
            client_username = request[ACCOUNT_NAME]
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(client_username)
            self.send_data(response, client_socket)

        elif ACTION in request and request[ACTION] == GET_ALL_USERS and ACCOUNT_NAME in request:
            response = RESPONSE_202
            response[LIST_INFO] = [username for username, last_connection_time in self.database.get_all_users()]
            self.send_data(response, client_socket)

        elif ACTION in request and request[ACTION] == GET_ACTIVE_USERS and ACCOUNT_NAME in request:
            response = RESPONSE_202
            response[LIST_INFO] = [
                username for username, ip, port, last_connection_time in self.database.get_active_users()
            ]
            self.send_data(response, client_socket)

        elif ACTION in request and request[ACTION] == ADD_CONTACT and ACCOUNT_NAME in request and CONTACT_NAME in request:
            client_username = request[ACCOUNT_NAME]
            contact_username = request[CONTACT_NAME]
            try:
                self.database.add_contact(client_username, contact_username)
            except ServerError as e:
                response = RESPONSE_400
                response[ERROR] = f'{e}'
                self.send_data(response, client_socket)
                logger.info(e)
            else:
                logger.info(f'{client_username} add contact {contact_username}')
                self.send_data(RESPONSE_200, client_socket)

        elif ACTION in request and request[ACTION] == REMOVE_CONTACT and \
                ACCOUNT_NAME in request and CONTACT_NAME in request:
            client_username = request[ACCOUNT_NAME]
            contact_username = request[CONTACT_NAME]
            try:
                self.database.remove_contact(client_username, contact_username)
            except ServerError as e:
                response = RESPONSE_400
                response[ERROR] = f'{e}'
                self.send_data(response, client_socket)
                logger.info(e)
            else:
                logger.info(f'{client_username} removed contact {contact_username}')
                self.send_data(RESPONSE_200, client_socket)
        else:
            self.send_data(RESPONSE_400, client_socket)
            logger.info(ERROR)

    def client_logout(self, client_socket):
        for username in self.client_usernames:
            if self.client_usernames[username] == client_socket:
                self.database.user_logout(username)
                del self.client_usernames[username]
                break
        self.clients.remove(client_socket)

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
                logger.e(f'Socket error: {e.args}')

            if clients_senders:
                for client in clients_senders:
                    try:
                        received_message = self.receive_data(client)
                        self.handle_request(received_message, client)
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
                    if client_name in self.client_usernames.keys() and client == self.client_usernames[client_name]:
                        try:
                            self.send_data(data_to_send, client)
                        except Exception as e:
                            logger.info(f'{client.getpeername()}: connection lost: {e.args}')
                            self.client_logout(client)


def arg_parser(default_ip_address, default_port):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default=default_ip_address, nargs='?',
                        help=f'server ip-address, default - {default_ip_address}')
    parser.add_argument('-p', '--port', default=default_port, type=int, nargs='?',
                        help=f'server port, default - {default_port}')

    cmd_args = parser.parse_args()
    ip_address = cmd_args.address
    port = cmd_args.port
    return ip_address, port


def config_load():
    """Парсер конфигурационного ini файла."""
    config = configparser.ConfigParser()
    config_path = os.path.join(BASE_DIR, 'server', 'server.ini')
    config.read(config_path)

    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', LISTEN_ADDRESS)
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'db_server.sqlite')
        return config


def main():
    config_path = os.path.join(BASE_DIR, 'server', 'server.ini')
    config = config_load()
    config.read(config_path)

    listen_address, listen_port = arg_parser(
        config['SETTINGS']['Listen_Address'], config['SETTINGS']['Default_port'])

    database_path = os.path.join(
        config['SETTINGS']['Database_path'],
        config['SETTINGS']['Database_file'])
    database = ServerDB(database_path)

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = ServerMainWindow(config, database)
    server_app.exec_()


if __name__ == '__main__':
    main()
