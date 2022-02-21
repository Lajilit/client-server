import binascii
import hashlib
import hmac
import json
import os
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from PyQt5.QtCore import QObject, pyqtSignal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(BASE_DIR)

from common.constants import ACTION, PRESENCE, TIME, ACCOUNT_NAME, RESPONSE, ALERT, LIST_INFO, ERROR, MESSAGE, SENDER, \
    MESSAGE_TEXT, DESTINATION, EXIT, GET_CONTACTS, ADD_CONTACT, CONTACT_NAME, REMOVE_CONTACT, \
    GET_ALL_USERS, USER, PUBLIC_KEY, DATA, RESPONSE_511, PUBLIC_KEY_REQUEST
from common.errors import ServerError, ConnectionTimeoutError, RequiredFieldMissedError, WrongResponseCodeError
from common.socket_include import MySocket
from project_logging.log_config import client_logger as logger


socket_lock = threading.Lock()


class ServerInteractionThread(threading.Thread, QObject, MySocket):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()
    response_205 = pyqtSignal()

    def __init__(self, ip_address, port, client_db, client_name, client_password, keys):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        MySocket.__init__(self)
        self.authorized = False
        self.name = client_name
        self.client_password = client_password
        self.database = client_db
        self.keys = keys
        self.socket = None
        self.connect_to_server(ip_address, port)
        self.log_in()
        if self.authorized:
            try:
                self.load_data()
            except OSError as e:
                if e.errno:
                    logger.critical(f'{self.name}: server connection lost')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    logger.debug(f'{self.name}: server connection timeout')

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
        logger.debug(f'{self.name}: connection established')

    def create_presence_message(self, public_key):
        presence_message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.name,
                PUBLIC_KEY: public_key
            }
        }
        logger.info(f'{self.name}: {PRESENCE} message is created')
        return presence_message

    def get_password_hash(self):
        password_bytes = self.client_password.encode('utf-8')
        salt = self.name.lower().encode('utf-8')
        password_hash = hashlib.pbkdf2_hmac('sha512', password_bytes, salt, 10000)
        password_hash_string = binascii.hexlify(password_hash)
        logger.debug(f'{self.name}: password hash ready')
        return password_hash_string

    def log_in(self):
        logger.debug(f'{self.name}: starting log_in dialog')
        public_key = self.keys.publickey().export_key().decode('ascii')
        password = self.get_password_hash()
        presence_response = self.communicate_server(self.create_presence_message(public_key))
        logger.info(f'{self.name}: the response from the server is being handled')
        if presence_response[RESPONSE] == 400:
            raise ServerError(presence_response[ERROR])
        elif presence_response[RESPONSE] == 511:
            password = hmac.new(password, presence_response[DATA].encode('utf-8'), 'MD5')
            digest = password.digest()
            answer = RESPONSE_511
            answer[DATA] = binascii.b2a_base64(digest).decode('ascii')
            authorize_response = self.communicate_server(answer)
            logger.info(f'{self.name}: the response from the server is being handled')
            if authorize_response[RESPONSE] == 400:
                raise ServerError(authorize_response[ERROR])
            elif authorize_response[RESPONSE] == 200:
                self.authorized = True
                logger.info(f'{self.name}: authorized')
            else:
                logger.info(f'{self.name}: Received wrong {RESPONSE} code: {authorize_response[RESPONSE]}')
                raise WrongResponseCodeError(authorize_response[RESPONSE])
        else:
            logger.info(f'{self.name}: Received unknown {RESPONSE} code: {presence_response[RESPONSE]}')
            raise WrongResponseCodeError(presence_response[RESPONSE])

    def get_public_key(self, contact_name):
        logger.debug(f'{self.name}: get public key request {contact_name}')
        request = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: contact_name
        }
        response = self.communicate_server(request)
        if RESPONSE in response and response[RESPONSE] == 511:
            return response[DATA]
        else:
            logger.error(f'{self.name}: no public key')

    def communicate_server(self, request):
        with socket_lock:
            try:
                self.send_data(request)
                logger.info(
                    f'{self.name}: {request[ACTION] if request.get(ACTION) else request} message was sent to the server'
                )
                result = self.receive_data()
            except OSError as e:
                if e.errno:
                    error = f'{self.name}: failed {request[ACTION]}: {e}'
                    logger.critical(error)
                    raise ServerError(error)
                error = f'{self.name}: failed {request[ACTION]}: {e}'
                logger.error(error)
                raise ConnectionTimeoutError(error)
            except (
                    ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError
            ) as e:
                error = f'{self.name}: failed {request[ACTION]}: {e}'
                logger.critical(error)
                raise ServerError(error)
            return result

    def handle_message(self, message):
        logger.info(f'{self.name}: the receives message is being handled')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.load_data()
                self.response_205.emit()
            else:
                logger.info(f'{self.name}: Received unknown {RESPONSE} code: {message[RESPONSE]}')
                raise WrongResponseCodeError(message[RESPONSE])
        elif ACTION in message and \
                message[ACTION] == MESSAGE and \
                SENDER in message and \
                MESSAGE_TEXT in message and \
                DESTINATION in message and \
                message[DESTINATION] == self.name:
            logger.info(f'{self.name}: Received a response from the user {message[SENDER]}')
            try:
                self.database.save_message(message[SENDER], self.name, message[MESSAGE_TEXT])
            except Exception as e:
                logger.e(f'{self.name}: Database error: {e}')
            else:
                self.new_message.emit(message[SENDER])
        else:
            logger.debug(f'{self.name}: the received message is incorrect: {message}')
            raise RequiredFieldMissedError(ACTION)

    def send_message(self, destination, message_text):
        message = {
            ACTION: MESSAGE,
            TIME: time.time(),
            SENDER: self.name,
            DESTINATION: destination,
            MESSAGE_TEXT: message_text
        }
        logger.debug(f'{self.name}: message is created: {message}')
        response = self.communicate_server(message)
        logger.info(f'{self.name}: the response from the server is being handled')
        if RESPONSE in response:
            if response[RESPONSE] == 200:
                return response[ALERT]
            elif response[RESPONSE] == 404:
                return response[ERROR]
            else:
                logger.info(f'{self.name}: Received wrong {RESPONSE} code: {response[RESPONSE]}')
                raise WrongResponseCodeError(response[RESPONSE])
        else:
            logger.debug(f'{self.name}: the response from server is incorrect: {response}')
            raise RequiredFieldMissedError(RESPONSE)

    def get_users_list(self, action):
        logger.debug(f'{self.name}: {action}')
        request = {
            ACTION: action,
            TIME: time.time(),
            ACCOUNT_NAME: self.name
        }
        response = self.communicate_server(request)
        logger.info(f'{self.name}: the response from the server is being handled')
        if RESPONSE in response:
            if response[RESPONSE] == 202:
                return response[LIST_INFO]
            elif response[RESPONSE] == 400:
                raise ServerError(response[ERROR])
            else:
                logger.info(f'{self.name}: Received wrong {RESPONSE} code: {response[RESPONSE]}')
                raise WrongResponseCodeError(response[RESPONSE])
        else:
            logger.debug(f'{self.name}: the response from server is incorrect: {response}')
            raise RequiredFieldMissedError(RESPONSE)

    def load_data(self):
        try:
            users_list = self.get_users_list(GET_ALL_USERS)
            logger.debug(f'{self.name}: server response: {users_list}')
            contacts_list = self.get_users_list(GET_CONTACTS)
            logger.debug(f'{self.name}: server response: {contacts_list}')
        except ServerError as e:
            logger.error(e.error_text)
        else:
            self.database.refresh_known_users(users_list)
            for contact in contacts_list:
                self.database.add_contact(contact)

    def add_contact(self, contact_name):
        logger.debug(f'{self.name}: add new contact {contact_name}')
        request = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            ACCOUNT_NAME: self.name,
            CONTACT_NAME: contact_name
        }
        response = self.communicate_server(request)
        logger.info(f'{self.name}: the response from the server is being handled')
        if RESPONSE in response:
            if response[RESPONSE] == 200:
                logger.debug(f'{self.name}: contact {contact_name} added successfully: {response}')
                self.database.add_contact(contact_name)
            elif response[RESPONSE] == 400:
                raise ServerError(response[ERROR])
            else:
                logger.info(f'{self.name}: Received wrong {RESPONSE} code: {response[RESPONSE]}')
                raise WrongResponseCodeError(response[RESPONSE])
        else:
            logger.debug(f'{self.name}: the response from server is incorrect: {response}')
            raise RequiredFieldMissedError(RESPONSE)

    def remove_contact(self, contact_name):
        logger.debug(f'{self.name}: the contact {contact_name} is removed from database')
        request = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            ACCOUNT_NAME: self.name,
            CONTACT_NAME: contact_name
        }
        response = self.communicate_server(request)
        logger.info(f'{self.name}: the response from the server is being handled')
        if RESPONSE in response:
            if response[RESPONSE] == 200:
                logger.debug(f'{self.name}: contact {contact_name} removed successfully: {response}')
                self.database.remove_contact(contact_name)
            elif response[RESPONSE] == 400:
                raise ServerError(response[ERROR])
            else:
                logger.info(f'{self.name}: Received wrong {RESPONSE} code: {response[RESPONSE]}')
                raise WrongResponseCodeError(response[RESPONSE])
        else:
            logger.debug(f'{self.name}: the response from server is incorrect: {response}')
            raise RequiredFieldMissedError(RESPONSE)

    def get_message(self):
        try:
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
            self.handle_message(message)

    def terminate_interaction(self):
        request = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.name
        }
        logger.info(
            f'{self.name}: {EXIT} request is created'
        )
        self.running = False
        with socket_lock:
            try:
                self.send_data(request)
            except OSError:
                pass
        logger.debug(f'{self.name}: server interaction process is terminated')
        time.sleep(0.5)

    def run(self):
        logger.debug(f'{self.name}: Receiver process started')
        while self.running:
            time.sleep(1)
            with socket_lock:
                self.socket.settimeout(0.5)
                self.get_message()
                self.socket.settimeout(5)
