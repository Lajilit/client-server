import argparse
import json
import socket
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from client_old.client_database import ClientDB
from common.constants import DEFAULT_IP, DEFAULT_PORT, ACTION, PRESENCE, TIME, \
    USERNAME, RESPONSE, ERROR, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, EXIT, ADD_CONTACT, \
    REMOVE_CONTACT, GET_ALL_USERS, LIST_INFO, GET_CONTACTS, GET_ACTIVE_USERS, CONTACT_NAME, ALERT
from project_logging.log_config import client_logger as logger
from common.socket_include import MySocket, SocketType
from common.errors import RequiredFieldMissedError, ServerError, IncorrectDataReceivedError, UnknownUserError

sock_lock = threading.Lock()
database_lock = threading.Lock()


class Client(MySocket):
    socket_type = SocketType('Client')

    def __init__(self, name, server_ip_address, server_port):
        super().__init__()
        self.name = name
        self.port = server_port
        self.host = server_ip_address
        self.database = None
        self.socket = None

    class ClientSender(threading.Thread, MySocket):
        def __init__(self, client_name, client_socket, client_db):
            super().__init__()
            self.name = client_name
            self.socket = client_socket
            self.database = client_db

        @staticmethod
        def help_function():
            print('Commands used:')
            print('message - command to send message')
            print('history - message history')
            print('contacts - contacts list')
            print('add - add new contact to list')
            print('del - remove contact from list')
            print('exit - command to exit')

        def create_message(self):
            destination = input('Message recipient: ')
            message_text = input('Enter your message text or press enter to shutdown: ')
            with database_lock:
                if not self.database.check_user_is_known(destination):
                    raise UnknownUserError({destination})
            message = {
                ACTION: MESSAGE,
                TIME: time.time(),
                SENDER: self.name,
                DESTINATION: destination,
                MESSAGE_TEXT: message_text
            }
            logger.debug(
                f'{self.name}: message is created: {message}'
            )
            return message

        def send_message(self, message):
            try:
                self.send_data(message, self.socket)
            except ConnectionRefusedError:
                logger.critical(
                    f'{self.name}: server connection lost'
                )
                sys.exit(1)
            except OSError as e:
                if e.errno:
                    logger.critical(f'{self.name}: server connection lost')
                    sys.exit(1)
                else:
                    logger.error(f'{self.name}: Connection timeout')
            else:
                answer = self.receive_data(self.socket)
                if RESPONSE in answer:
                    if answer[RESPONSE] == 200:
                        logger.debug(f'{self.name}: message was sent to user {message[DESTINATION]}')
                        with database_lock:
                            self.database.save_message(self.name, message[DESTINATION], message[MESSAGE_TEXT])
                    elif answer[RESPONSE] == 400:
                        logger.debug(answer[ERROR])

        def create_exit_request(self):
            message = {
                ACTION: EXIT,
                TIME: time.time(),
                USERNAME: self.name
            }
            logger.info(
                f'{self.name}: {EXIT} message is created'
            )
            return message

        def get_active_users(self):
            logger.debug(f'{self.name}: get active users list from server')
            request = {
                ACTION: GET_ACTIVE_USERS,
                TIME: time.time(),
                USERNAME: self.name
            }
            try:
                self.send_data(request, self.socket)
            except ServerError:
                logger.error('Error sending information to the server')
            else:
                answer = self.receive_data(self.socket)
                if RESPONSE in answer:
                    if answer[RESPONSE] == 202:
                        return answer[LIST_INFO]
                    else:
                        raise ServerError(answer[ERROR])
                raise RequiredFieldMissedError(RESPONSE)

        def add_contact(self):
            new_contact = input('Enter new contact username: ')
            if not self.database.check_user_is_a_contact(new_contact):
                request = {
                    ACTION: ADD_CONTACT,
                    TIME: time.time(),
                    USERNAME: username,
                    CONTACT_NAME: new_contact
                }
                try:
                    self.send_data(request, self.socket)
                except ServerError:
                    logger.error('Error sending information to the server')
                else:
                    answer = self.receive_data(self.socket)
                    if RESPONSE in answer and answer[RESPONSE] == 200:
                        print('Contact created successfully')
                        with database_lock:
                            self.database.add_contact(new_contact)
                    else:
                        raise ServerError(answer[ERROR])
            else:
                logger.error('Contact already exists')

        def remove_contact(self):
            contact_to_delete = input('Enter username of the contact to delete: ')
            if self.database.check_user_is_a_contact(contact_to_delete):
                logger.debug(f'{self.name}: the contact {contact_to_delete} is removed from database')
                request = {
                    ACTION: REMOVE_CONTACT,
                    TIME: time.time(),
                    USERNAME: username,
                    CONTACT_NAME: contact_to_delete
                }
                try:
                    self.send_data(request, self.socket)
                except ServerError:
                    logger.error('Error sending information to the server')
                else:
                    answer = self.receive_data(self.socket)
                    if RESPONSE in answer and answer[RESPONSE] == 200:
                        print('Contact is removed successfully')
                        with database_lock:
                            self.database.remove_contact(contact_to_delete)
                    else:
                        raise ServerError('Contact removing error')
            else:
                logger.error('Contact does not exist')

        def print_history(self, ):
            contact_name = input(
                'Enter contact name to show its message history oe press Enter to show all message history ')
            with database_lock:
                if contact_name:
                    if not self.database.check_user_is_known(contact_name):
                        raise UnknownUserError({contact_name})
                    history_list = self.database.get_user_message_history(self.name, contact_name)
                else:
                    history_list = self.database.get_user_message_history(self.name)
                if history_list:
                    for user_from, user_to, message_text, message_time in history_list:
                        print(f'\n{message_time}\nFrom: {user_from} to {user_to}:\n{message_text}')
                else:
                    print('Message history is empty')

        def run(self):
            self.help_function()
            while True:
                command = input('Enter command: ')
                if command == 'message':
                    with sock_lock:
                        try:
                            active_users = self.get_active_users()
                        except (ServerError, RequiredFieldMissedError) as e:
                            logger.error(e)
                        else:
                            print(f'Active users are: {active_users}')
                    try:
                        message = self.create_message()
                    except UnknownUserError as e:
                        logger.error(e)
                        continue
                    with sock_lock:
                        self.send_message(message)

                elif command == 'exit':
                    message = self.create_exit_request()
                    with sock_lock:
                        try:
                            self.send_data(message, self.socket)
                            logger.info(
                                f'{self.name}: {EXIT} message was sent to the server'
                            )
                        except ConnectionRefusedError as e:
                            logger.critical(e)
                            logger.critical(
                                f'{self.name}: server connection lost'
                            )
                    print('Connection closed')
                    logger.info(f'{self.name}: connection closed')
                    time.sleep(0.5)
                    break
                elif command == 'contacts':
                    with database_lock:
                        contacts_list = self.database.get_contacts()
                    if contacts_list:
                        for contact in contacts_list:
                            print(contact)
                    else:
                        print('Contacts list is empty')
                elif command == 'add':
                    with sock_lock:
                        try:
                            self.add_contact()
                        except ServerError as e:
                            print(e)
                elif command == 'del':
                    with sock_lock:
                        try:
                            self.remove_contact()
                        except ServerError as e:
                            print(e)
                elif command == 'history':
                    try:
                        self.print_history()
                    except UnknownUserError as e:
                        print(e)
                elif command == 'help':
                    self.help_function()
                else:
                    print('Wrong command. Print help to show available commands')

    class ClientReceiver(threading.Thread, MySocket):
        def __init__(self, client_name, client_socket, client_db):
            super().__init__()
            self.name = client_name
            self.socket = client_socket
            self.database = client_db

        def run(self):
            while True:
                time.sleep(2)
                with sock_lock:
                    try:
                        message = self.receive_data(self.socket)
                    except IncorrectDataReceivedError as e:
                        logger.debug(e)
                    except OSError as e:
                        if e.errno:
                            logger.critical(f'{self.name}: server connection lost')
                            break
                    except (ConnectionError,
                            ConnectionAbortedError,
                            ConnectionResetError,
                            json.decoder.JSONDecodeError):
                        logger.critical(f'{self.name}: server connection lost')
                        break
                    else:
                        logger.debug(f'{self.name}: the message {message} is being handled')
                        if ACTION in message and \
                                message[ACTION] == MESSAGE and \
                                SENDER in message and \
                                MESSAGE_TEXT in message and \
                                DESTINATION in message and \
                                message[DESTINATION] == self.name:
                            logger.debug(
                                f'{self.name}: Received a message from the user '
                                f'{message[SENDER]}: {message[MESSAGE_TEXT]}'
                            )
                            print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
                            with database_lock:
                                try:
                                    self.database.save_message(message[SENDER], self.name, message[MESSAGE_TEXT])
                                except Exception as e:
                                    print(e)
                                    logger.error('Database error')
                        else:
                            logger.info(
                                f'{self.name}: the message from server is incorrect:'
                                f' {message}')

    def create_presence_message(self):
        message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USERNAME: self.name,
        }
        logger.info(f'{self.name}: {PRESENCE} message is created')
        return message

    def handle_response(self, message):
        logger.info(
            f'{self.name}: the response from the server is being handled'
        )
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return message[ALERT]
            elif message[RESPONSE] == 202:
                return message[LIST_INFO]
            else:
                raise ServerError(message[ERROR])
        raise RequiredFieldMissedError(RESPONSE)

    def create_get_all_users_request(self):
        logger.debug(f'{self.name}: get all users list from server')
        message = {
            ACTION: GET_ALL_USERS,
            TIME: time.time(),
            USERNAME: self.name
        }
        return message

    def create_get_contacts_request(self):
        logger.debug(f'{self.name}: get user contacts list from server')
        message = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USERNAME: self.name
        }
        return message

    def communicate_server(self, message):
        self.send_data(message, self.socket)
        logger.info(f'{self.name}: {message[ACTION]} message was sent to the server')
        return self.handle_response(self.receive_data(self.socket))

    def load_data(self):
        try:
            users_list = self.communicate_server(self.create_get_all_users_request())
            logger.debug(f'{self.name}: server response: {users_list}')
        except ServerError as e:
            logger.error(e)
        else:
            self.database.refresh_known_users(users_list)
        try:
            contacts_list = self.communicate_server(self.create_get_contacts_request())
            logger.debug(f'{self.name}: server response: {contacts_list}')

        except ServerError as e:
            logger.error(e)
        else:
            for contact in contacts_list:
                self.database.add_contact(contact)

    def start_client(self):
        print('Client module')
        logger.info(f'Client module started')
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.settimeout(2)
            self.socket.connect((self.host, self.port))
            logger.info(f'{self.name}: trying to connect to server at {self.host}:{self.port}')
            answer = self.communicate_server(self.create_presence_message())
            logger.debug(f'{self.name}: server response: {answer}')
        except json.decoder.JSONDecodeError as e:
            logger.error(f'JSONDecodeError: {e}')
            sys.exit(1)
        except ServerError as e:
            logger.error(f'Server error: {e}')
            sys.exit(1)
        except RequiredFieldMissedError as e:
            logger.error(f'RequiredFieldMissedError: {e}')
            sys.exit(1)
        except (ConnectionRefusedError, ConnectionError):
            logger.critical(
                f'{self.host}:{self.port}: no connection could be made because the target machine actively refused it')
            sys.exit(1)

        self.database = ClientDB(self.name)
        self.load_data()

        sender = self.ClientSender(self.name, self.socket, self.database)
        sender.daemon = True
        sender.start()
        logger.info(f'{self.name}: sender process started')

        receiver = self.ClientReceiver(self.name, self.socket, self.database)
        receiver.daemon = True
        receiver.start()
        logger.info(f'{self.name}: receiver process started')

        while True:
            time.sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default=DEFAULT_IP, nargs='?',
                        help=f'server ip-address, default - {DEFAULT_IP}')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'server port, default - {DEFAULT_PORT}')
    parser.add_argument('-n', '--name', default='Guest', nargs='?',
                        help='user name, default - Guest')
    cmd_args = parser.parse_args()
    ip_address = cmd_args.address
    port = cmd_args.port
    username = cmd_args.name

    client = Client(username, ip_address, port)
    client.start_client()
