import argparse
import configparser
import os
import sys

from PyQt5.QtWidgets import QApplication

from server.server_core import Server

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(BASE_DIR)

from common.constants import DEFAULT_PORT, LISTEN_ADDRESS
from server.server_database import ServerDB
from server.server_main_window import ServerMainWindow


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
    main_window = ServerMainWindow(config, server, database)
    server_app.exec_()


if __name__ == '__main__':
    main()
