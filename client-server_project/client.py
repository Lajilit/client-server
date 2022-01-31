import argparse
import sys
from PyQt5.QtWidgets import QApplication

from common.constants import DEFAULT_IP, DEFAULT_PORT
from common.errors import ServerError
from client.client_database import ClientDB
from client.server_interaction import ClientServerInteraction
from client.main_window import ClientMainWindow
from client.start_dialog import StartDialog

from project_logging.log_config import client_logger as logger


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default=DEFAULT_IP, nargs='?',
                        help=f'server ip-address, default - {DEFAULT_IP}')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?',
                        help=f'server port, default - {DEFAULT_PORT}')
    parser.add_argument('-n', '--name', default=None, nargs='?',
                        help='user name, default - Guest')
    cmd_args = parser.parse_args()
    ip_address = cmd_args.address
    port = cmd_args.port
    username = cmd_args.name

    # проверим подходящий номер порта
    if not 1023 < port < 65536:
        logger.critical(
            f'Error. The port must be a number between 1024 and 65535. Client shutdown')
        exit(1)

    return ip_address, port, username


if __name__ == '__main__':
    server_address, server_port, client_name = arg_parser()
    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = StartDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.ui.input_username.text()
            del start_dialog
        else:
            exit(0)

    logger.info(f'{client_name}: Client started (server ip {server_address} , server port: {server_port})')

    database = ClientDB(client_name)
    try:
        server_int = ClientServerInteraction(server_address, server_port, client_name, database)
    except ServerError as e:
        logger.info(e)
        exit(1)
    else:
        server_int.setDaemon(True)
        server_int.start()

        main_window = ClientMainWindow(database, server_int)
        main_window.make_connection(server_int)
        main_window.setWindowTitle(f'Messenger - user {client_name}')
        client_app.exec_()

        server_int.terminate_interaction()
        server_int.join()
