import binascii
import hmac
import os
import select
import sys
import threading
from _socket import SO_REUSEADDR
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM
from sqlite3 import IntegrityError
from ssl import SOL_SOCKET

from common.errors import ServerError

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(BASE_DIR)

from common.constants import MAX_CONNECTIONS, ACTION, PRESENCE, TIME, \
    ACCOUNT_NAME, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, ERROR, RESPONSE_200, RESPONSE_400, EXIT, ADD_CONTACT, \
    REMOVE_CONTACT, GET_ALL_USERS, RESPONSE_202, LIST_INFO, \
    GET_CONTACTS, CONTACT_NAME, GET_ACTIVE_USERS, RESPONSE_404, LISTEN_ADDRESS, USER, RESPONSE_511, DATA, RESPONSE, \
    PUBLIC_KEY, PUBLIC_KEY_REQUEST, RESPONSE_205
from common.socket_include import MySocket, SocketType, CheckServerPort
from project_logging.log_config import server_logger as logger


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

        if self.host != LISTEN_ADDRESS:
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
        if ACTION in request and request[ACTION] == PUBLIC_KEY_REQUEST and ACCOUNT_NAME in request:
            logger.info(
                f'{client_socket.getpeername()}: {PUBLIC_KEY_REQUEST} request'
            )
            contact_name = request[ACCOUNT_NAME]
            logger.info(
                f'{client_socket.getpeername()}: contact_name {contact_name}'
            )
            response = RESPONSE_511
            response[DATA] = self.database.get_public_key(contact_name)
            if response[DATA]:
                try:
                    self.send_data(response, client_socket)
                    logger.info(f'{client_socket.getpeername()}: ok')
                except OSError:
                    self.client_logout(contact_name)
            else:
                response = RESPONSE_400
                response[ERROR] = 'No public key for the user'
                try:
                    self.send_data(response, client_socket)
                    logger.info(f'{client_socket.getpeername()}: response[ERROR]')
                except OSError:
                    self.client_logout(contact_name)

        elif ACTION in request and request[ACTION] == PRESENCE and TIME in request and USER in request:
            contact_name = request[USER][ACCOUNT_NAME]
            client_ip, client_port = client_socket.getpeername()
            public_key = request[USER][PUBLIC_KEY]
            if contact_name in self.client_usernames.keys():
                response = RESPONSE_400
                response[ERROR] = 'Username already in use'
                self.send_data(response, client_socket)
                self.clients.remove(client_socket)
                client_socket.close()
            elif not self.database.check_user_exists(contact_name):
                response = RESPONSE_400
                response[ERROR] = 'Username is not registred on server'
                self.send_data(response, client_socket)
                self.clients.remove(client_socket)
                client_socket.close()
            else:
                logger.info(
                    f'{client_ip}:{client_port}: name \'{contact_name}\'')
                response = RESPONSE_511
                random_str = binascii.hexlify(os.urandom(64))
                response[DATA] = random_str.decode('ascii')
                hash = hmac.new(self.database.get_hash(contact_name), random_str, 'MD5')
                server_digest = hash.digest()
                logger.debug(f'{client_ip}:{client_port}: auth response = {response}')
                self.send_data(response, client_socket)
                answer = self.receive_data(client_socket)
                client_digest = binascii.a2b_base64(answer[DATA])
                if RESPONSE in answer and answer[RESPONSE] == 511 and hmac.compare_digest(server_digest, client_digest):
                    self.client_usernames[contact_name] = client_socket
                    logger.info(
                        f'{client_ip}:{client_port}: '
                        f'name \'{contact_name}\' added into clients_usernames'
                    )
                    try:
                        self.send_data(RESPONSE_200, client_socket)
                    except OSError:
                        self.client_logout(contact_name)
                    self.database.user_login(contact_name, client_ip, client_port, public_key)
                    logger.info(f'{contact_name} login')
                    with conflag_lock:
                        new_connection = True
                else:
                    response = RESPONSE_400
                    response[ERROR] = 'Wrong password'
                    try:
                        self.send_data(response, client_socket)
                    except OSError:
                        pass
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
            contact_name = request[ACCOUNT_NAME]
            logger.info(f'{contact_name} exit')
            del self.client_usernames[contact_name]
            self.database.user_logout(contact_name)
            self.clients.remove(client_socket)
            client_socket.close()
            with conflag_lock:
                new_connection = True

        elif ACTION in request and request[ACTION] == GET_CONTACTS and ACCOUNT_NAME in request:
            contact_name = request[ACCOUNT_NAME]
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(contact_name)
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

        elif ACTION in request and request[ACTION] == ADD_CONTACT and \
                ACCOUNT_NAME in request and CONTACT_NAME in request:
            contact_name = request[ACCOUNT_NAME]
            contact_username = request[CONTACT_NAME]
            try:
                self.database.add_contact(contact_name, contact_username)
            except ServerError as e:
                response = RESPONSE_400
                response[ERROR] = f'{e}'
                self.send_data(response, client_socket)
                logger.info(e)
            else:
                logger.info(f'{contact_name} add contact {contact_username}')
                self.send_data(RESPONSE_200, client_socket)

        elif ACTION in request and request[ACTION] == REMOVE_CONTACT and \
                ACCOUNT_NAME in request and CONTACT_NAME in request:
            contact_name = request[ACCOUNT_NAME]
            contact_username = request[CONTACT_NAME]
            try:
                self.database.remove_contact(contact_name, contact_username)
            except ServerError as e:
                response = RESPONSE_400
                response[ERROR] = f'{e}'
                self.send_data(response, client_socket)
                logger.info(e)
            else:
                logger.info(f'{contact_name} removed contact {contact_username}')
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

    def send_service_update_message(self):
        '''Метод реализующий отправки сервисного сообщения 205 клиентам.'''
        for client in self.client_usernames:
            try:
                self.send_data(RESPONSE_205, self.client_usernames[client])
            except OSError:
                self.client_logout(self.client_usernames[client])

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