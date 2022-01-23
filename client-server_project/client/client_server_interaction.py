import json
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from PyQt5.QtCore import QObject, pyqtSignal

from constants import ACTION, PRESENCE, TIME, USERNAME, RESPONSE, ALERT, LIST_INFO, ERROR, MESSAGE, SENDER, \
    MESSAGE_TEXT, DESTINATION, EXIT, GET_ACTIVE_USERS, GET_CONTACTS, ADD_CONTACT, CONTACT_NAME, REMOVE_CONTACT
from errors import ServerError
from socket_include import MySocket
from project_logging.config.log_config import client_logger as logger

socket_lock = threading.Lock()


class ClientServerInteraction(threading.Thread, QObject, MySocket):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, ip_address, port, client_name, client_db):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        MySocket.__init__(self)
        self.name = client_name
        self.database = client_db
        self.socket = None
        self.connect_to_server(ip_address, port)
        try:
            self.load_data()
        except OSError as e:
            if e.errno:
                logger.critical(f'{self.name}: server connection lost')
                self.running = False
                self.connection_lost.emit()
        except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
            logger.critical(f'{self.name}: server connection lost')
            self.running = False
            self.connection_lost.emit()
        else:
            self.running = True

    def connect_to_server(self, ip, port):
        logger.info(f'{self.name}: client module started')
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(5)
        connected = False
        for i in range(5):
            logger.info(f'{self.name}: attempt to connect to server at {ip}:{port} #{i+1}')
            try:
                self.socket.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)
        if not connected:
            error = f'{self.name}: failed to connect to the server'
            logger.critical(error)
            raise ServerError(error)
        try:
            result = self.communicate_server(self.create_presence_message())
        except (OSError, json.JSONDecodeError):
            error = f'{self.name}: server connection lost'
            logger.critical(error)
            raise ServerError(error)
        else:
            logger.info(f'{self.name}: connection established: {result}')

    def communicate_server(self, request):
        with socket_lock:
            self.send_data(request)
            logger.info(f'{self.name}: {request[ACTION]} message was sent to the server')
            return self.handle_response(self.receive_data())

    def create_presence_message(self):
        presence_message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USERNAME: self.name,
        }
        logger.info(f'{self.name}: {PRESENCE} message is created')
        return presence_message

    def create_exit_request(self):
        request = {
            ACTION: EXIT,
            TIME: time.time(),
            USERNAME: self.name
        }
        logger.info(
            f'{self.name}: {EXIT} request is created'
        )
        return request

    def handle_response(self, response):
        logger.info(f'{self.name}: the response from the server is being handled')
        if RESPONSE in response:
            if response[RESPONSE] == 200:
                return response[ALERT]
            elif response[RESPONSE] == 202:
                return response[LIST_INFO]
            elif response[RESPONSE] == 400:
                raise ServerError(response[ERROR])
            elif response[RESPONSE] == 404:
                return response[ERROR]
            else:
                logger.info(f'{self.name}: Received unknown {RESPONSE} code: {response[RESPONSE]}')

        elif ACTION in response and \
                response[ACTION] == MESSAGE and \
                SENDER in response and \
                MESSAGE_TEXT in response and \
                DESTINATION in response and \
                response[DESTINATION] == self.name:
            logger.info(f'{self.name}: Received a response from the user {response[SENDER]}')
            try:
                self.database.save_message(response[SENDER], self.name, response[MESSAGE_TEXT])
            except Exception as e:
                logger.error(f'{self.name}: Database error: {e}')
            else:
                self.new_message.emit(response[SENDER])
        else:
            logger.debug(f'{self.name}: the response from server is incorrect: {response}')

    def create_message(self, destination, message_text):
        message = {
            ACTION: MESSAGE,
            TIME: time.time(),
            SENDER: self.name,
            DESTINATION: destination,
            MESSAGE_TEXT: message_text
        }
        logger.debug(f'{self.name}: message is created: {message}')
        return message

    def send_message(self, message):
        server_response = self.communicate_server(message)
        if server_response == 'ok':
            logger.debug(f'{self.name}: message was sent to user {message[DESTINATION]}')
            self.database.save_message(self.name, message[DESTINATION], message[MESSAGE_TEXT])
        else:
            logger.debug(server_response)

    def get_active_users(self):
        logger.debug(f'{self.name}: get active users list from server')
        request = {
            ACTION: GET_ACTIVE_USERS,
            TIME: time.time(),
            USERNAME: self.name
        }
        try:
            active_users_list = self.communicate_server(request)
        except ServerError as e:
            logger.error(f'{self.name}: failed to get list of active users: {e}')
        else:
            return active_users_list

    def get_contacts(self):
        logger.debug(f'{self.name}: get user contacts list from server')
        request = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USERNAME: self.name
        }
        try:
            user_contacts = self.communicate_server(request)
        except ServerError as e:
            logger.error(f'{self.name}: failed to get contacts list: {e}')
        else:
            return user_contacts

    def load_data(self):
        try:
            users_list = self.get_active_users()
            logger.debug(f'{self.name}: server response: {users_list}')
        except ServerError as e:
            logger.error(e)
        else:
            self.database.refresh_known_users(users_list)
        try:
            contacts_list = self.get_contacts()
            logger.debug(f'{self.name}: server response: {contacts_list}')
        except ServerError as e:
            logger.error(e)
        else:
            for contact in contacts_list:
                self.database.add_contact(contact)

    def add_contact(self, contact_name):
        logger.debug(f'{self.name}: add new contact {contact_name}')
        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USERNAME: self.name,
            CONTACT_NAME: contact_name
        }
        try:
            result = self.communicate_server(request)
        except ServerError as e:
            logger.error(f'{self.name}: failed to add new contact: {e}')
        else:
            logger.debug(f'{self.name}: contact {contact_name} added successfully: {result}')
            self.database.add_contact(contact_name)

    def remove_contact(self, contact_name):
        logger.debug(f'{self.name}: the contact {contact_name} is removed from database')
        request = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USERNAME: self.name,
            CONTACT_NAME: contact_name
        }
        try:
            result = self.communicate_server(request)
        except ServerError as e:
            logger.error(f'{self.name}: failed to remove contact: {e}')
        else:
            logger.debug(f'{self.name}: contact {contact_name} removed successfully: {result}')
            self.database.remove_contact(contact_name)

    def terminate_interaction(self):
        self.running = False
        with socket_lock:
            try:
                self.send_data(self.create_exit_request())
            except OSError:
                pass
        logger.debug(f'{self.name}: server interaction process is terminated')
        time.sleep(0.5)

    def run(self):
        logger.debug(f'{self.name}: Receiver process started')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.socket.settimeout(0.5)
                    message = self.receive_data()
                except OSError as e:
                    if e.errno:
                        logger.critical(f'{self.name}: server connection lost')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    logger.critical(f'{self.name}: server connection lost')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    logger.debug(f'{self.name}: : Message {message} received from server')
                    self.handle_response(message)
                finally:
                    self.socket.settimeout(5)
