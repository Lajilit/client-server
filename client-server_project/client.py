import argparse
import inspect
import json
import socket
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from client_database import ClientDB
from constants import DEFAULT_IP, DEFAULT_PORT, ACTION, PRESENCE, TIME, USER, \
    ACCOUNT_NAME, STATUS, TYPE, RESPONSE, ERROR, MESSAGE, SENDER, DESTINATION, MESSAGE_TEXT, EXIT, ADD_CONTACT, \
    REMOVE_CONTACT
from project_logging.config.log_config import client_logger as logger
from socket_verifier import SocketVerifier
from socket_include import Socket, SocketType
from errors import RequiredFieldMissedError, ServerError, IncorrectDataReceivedError, UnknownUserError

socket_lock = threading.Lock()
database_lock = threading.Lock()


def log(some_function):
    def wrapper(*args, **kwargs):
        logger.debug(
            f'Function: {some_function.__name__}, args: {args}, kwargs: {kwargs}, '
            f'called from function: {inspect.stack()[1][3]}'
        )
        result = some_function(*args, **kwargs)
        return result

    return wrapper


class ClientMeta(metaclass=SocketVerifier):
    pass


class Client(ClientMeta, Socket):
    socket_type = SocketType('Client')

    def __init__(self, name, server_ip_address, server_port):
        super().__init__()
        self.name = name
        self.port = server_port
        self.host = server_ip_address
        self.database = ClientDB(self.name)

    @log
    def create_presence(self):
        output_message = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.name,
                STATUS: 'online'
            },
            TYPE: STATUS
        }
        logger.info(f'{self.name}: {PRESENCE} message is created')
        return output_message

    @log
    def handle_response(self, message):
        logger.info(
            f'{self.name}: the response from the server is being handled'
        )
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return f'OK'
            return f'{message[ERROR]}'
        raise RequiredFieldMissedError(RESPONSE)

    @staticmethod
    def help_function():
        print('Commands used:')
        print('message - command to send message')
        print('history - message history')
        print('contacts - contacts list')
        print('add - add new contact to list')
        print('del - remove contact from list')
        print('exit - command to exit')

    @log
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
        with database_lock:
            self.database.save_message(self.name, destination, message_text)
            print(message, destination)
        return message, destination

    @log
    def create_exit_message(self):
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.name
        }
        logger.info(
            f'{self.name}: {EXIT} message is created'
        )
        return message

    def add_contact(self):
        new_contact = input('Enter new contact username: ')
        if not self.database.check_user_is_a_contact(new_contact):
            with database_lock:
                self.database.add_contact(new_contact)
            with socket_lock:
                request = {
                    ACTION: ADD_CONTACT,
                    TIME: time.time(),
                    USER: username,
                    ACCOUNT_NAME: new_contact
                }
                try:
                    self.send_data(request, self.socket)
                except ServerError:
                    logger.error('Error sending information to the server')
                else:
                    answer = self.receive_data(self.socket)
                    if RESPONSE in answer and answer[RESPONSE] == 200:
                        print('Contact created successfully')
                    else:
                        raise ServerError('Contact creation error')
        else:
            logger.error('Contact already exists')

    def remove_contact(self):
        contact_to_delete = input('Enter username of the contact to delete: ')
        with database_lock:
            if self.database.check_user_is_a_contact(contact_to_delete):
                with database_lock:
                    self.database.remove_contact(contact_to_delete)
                    logger.debug(f'{self.name}: the contact {contact_to_delete} is removed from database')
                with socket_lock:
                    request = {
                        ACTION: REMOVE_CONTACT,
                        TIME: time.time(),
                        USER: username,
                        ACCOUNT_NAME: contact_to_delete
                    }
                    try:
                        self.send_data(request, self.socket)
                    except ServerError:
                        logger.error('Error sending information to the server')
                    else:
                        answer = self.receive_data(self.socket)
                        if RESPONSE in answer and answer[RESPONSE] == 200:
                            print('Contact is removed successfully')
                        else:
                            raise ServerError('Contact removing error')
            else:
                logger.error('Contact does not exist')

    @log
    def user_interaction(self):
        self.help_function()
        while True:
            command = input('Enter command: ')
            if command == 'message':
                try:
                    message, destination = self.create_message()
                except UnknownUserError as e:
                    logger.error(f'Unknown user: {e}')
                    continue
                with socket_lock:
                    try:
                        self.send_data(message, self.socket)
                        logger.debug(
                            f'{self.name}: message was sent to user {destination}'
                        )
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
            elif command == 'exit':
                message = self.create_exit_message()
                print(1)
                with socket_lock:
                    print(2)
                    try:
                        self.send_data(message, self.socket)
                        logger.info(
                            f'{self.name}: {EXIT} message was sent to the server'
                        )
                    except ConnectionRefusedError:
                        logger.critical(
                            f'{self.name}: server connection lost'
                        )
                        sys.exit(1)
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
                try:
                    self.add_contact()
                except ServerError as e:
                    print(e)
            elif command == 'del':
                try:
                    self.remove_contact()
                except ServerError as e:
                    print(e)
            elif command == 'history':
                pass
            elif command == 'help':
                self.help_function()
            else:
                print('Wrong command. Print help to show available commands')

    @log
    def listen_server(self):
        while True:
            time.sleep(1)
            # with socket_lock: TODO!!!
            try:
                message = self.receive_data(self.socket)
            except IncorrectDataReceivedError as e:
                logger.debug(e)
            except OSError as e:
                if e.errno:
                    logger.critical(f'{self.name}: server connection lost')
                    break
                else:
                    logger.error(f'{self.name}: Connection timeout')
            except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.decoder.JSONDecodeError):
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

    def start(self):
        print('Client module')
        logger.info(f'Client module started')
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f'{self.name}: trying to connect to server at {self.host}:{self.port}')
            self.send_data(self.create_presence(), self.socket)
            logger.info(f'{self.name}: presence message was sent to the server')
            answer = self.handle_response(self.receive_data(self.socket))
            logger.debug(
                f'{self.name}: server response: {answer}'
            )
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

        receiver = threading.Thread(target=self.listen_server)
        receiver.daemon = True
        receiver.start()
        logger.info(f'{self.name}: receiver process started')

        interface = threading.Thread(target=self.user_interaction)
        interface.daemon = True
        interface.start()
        logger.info(f'{self.name}: interface process started')

        while True:
            time.sleep(1)
            if receiver.is_alive() and interface.is_alive():
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
    client.start()
