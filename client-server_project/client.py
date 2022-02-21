import argparse
import os
import sys

from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(BASE_DIR)

from common.constants import DEFAULT_IP, DEFAULT_PORT
from common.errors import ServerError
from client.client_database import ClientDB
from client.server_interaction_thread import ServerInteractionThread
from client.client_main_window import ClientMainWindow
from client.client_login_dialog import StartDialog
from project_logging.log_config import client_logger as logger


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default=DEFAULT_IP, nargs='?',
                        help=f'server ip-address, default - {DEFAULT_IP}')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'server port, default - {DEFAULT_PORT}')
    parser.add_argument('-n', '--name', default='', nargs='?',
                        help='user name')
    parser.add_argument('-s', '--secret', default='', nargs='?',
                        help='user password')
    cmd_args = parser.parse_args()
    ip_address = cmd_args.address
    port = cmd_args.port
    username = cmd_args.name
    password = cmd_args.secret

    # проверим подходящий номер порта
    if not 1023 < port < 65536:
        logger.critical(
            f'Error. The port must be a number between 1024 and 65535. Client shutdown')
        exit(1)

    return ip_address, port, username, password


if __name__ == '__main__':
    server_address, server_port, client_name, client_password = arg_parser()
    client_app = QApplication(sys.argv)
    start_dialog = StartDialog()
    if not client_name or not client_password:
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.ui.input_username.text()
            client_password = start_dialog.ui.input_password.text()
        else:
            exit(0)

    logger.info(f'{client_name}: Client started (server ip {server_address} , server port: {server_port})')

    key_file = os.path.join(BASE_DIR, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    logger.debug(f'{client_name}: keys successfully loaded')

    database = ClientDB(client_name)
    try:
        server_int = ServerInteractionThread(server_address, server_port, database, client_name, client_password, keys)
    except ServerError as e:
        message = QMessageBox()
        message.critical(start_dialog, 'Server error', e.error_text)
        logger.info(e)
        exit(1)
    else:
        logger.debug(f'{client_name}: client-server interaction started')
        server_int.setDaemon(True)
        server_int.start()

        del start_dialog

        main_window = ClientMainWindow(client_name, database, server_int)

        client_app.exec_()

        server_int.terminate_interaction()
        server_int.join()
