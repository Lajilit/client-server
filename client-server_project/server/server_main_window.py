import configparser
import os
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication

from common.constants import DEFAULT_PORT, LISTEN_ADDRESS
from server.server_gui import ClientStatisticsWindow, ServerConfigWindow
from server.server_main_window_gui import Server_Ui_MainWindow

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)


class ServerMainWindow(QMainWindow):
    def __init__(self, config, database):
        super().__init__()
        self.config_window = None
        self.stat_window = None
        self.config = config
        self.db = database
        self.ui = Server_Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.exit_action.setShortcut('Ctrl+Q')
        self.ui.exit_action.triggered.connect(qApp.quit)
        self.ui.statusbar.showMessage('Server Working')

        self.ui.refresh_users_list_button.triggered.connect(self.update_active_users)
        self.ui.show_clients_statistics_button.triggered.connect(self.show_statistics)
        self.ui.show_server_configuration_button.triggered.connect(self.show_server_config)

        self.ui.active_clients_table.setModel(self.gui_create_active_users_table(self.db))
        self.ui.active_clients_table.resizeColumnsToContents()
        self.ui.active_clients_table.resizeRowsToContents()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_active_users)
        self.timer.start(1000)

        self.show()

    @staticmethod
    def gui_create_clients_statistics_table(db):
        clients_statistics = db.get_client_statistics()

        clients_statistics_table = QStandardItemModel()
        clients_statistics_table.setHorizontalHeaderLabels(
            ['Client username', 'Last connection time', 'Messages sent', 'Messages received'])
        for client in clients_statistics:
            username, last_connection_time, messages_sent, messages_received = client

            username = QStandardItem(username)
            username.setEditable(False)

            last_connection_time = QStandardItem(str(last_connection_time.replace(microsecond=0)))
            last_connection_time.setEditable(False)

            messages_sent = QStandardItem(str(messages_sent))
            messages_sent.setEditable(False)

            messages_received = QStandardItem(str(messages_received))
            messages_received.setEditable(False)

            clients_statistics_table.appendRow([username, last_connection_time, messages_sent, messages_received])
        return clients_statistics_table

    @staticmethod
    def gui_create_active_users_table(db):
        active_users = db.get_active_users()
        active_users_table = QStandardItemModel()
        active_users_table.setHorizontalHeaderLabels(['Client username', 'IP address', 'Port', 'Connection time'])
        for user in active_users:
            username, ip, port, time = user

            username = QStandardItem(username)
            username.setEditable(False)

            ip = QStandardItem(ip)
            ip.setEditable(False)

            port = QStandardItem(str(port))
            port.setEditable(False)

            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)

            active_users_table.appendRow([username, ip, port, time])
        return active_users_table

    def show_statistics(self):
        self.stat_window = ClientStatisticsWindow()
        self.stat_window.clients_statistics_table.setModel(self.gui_create_clients_statistics_table(self.db))
        self.stat_window.clients_statistics_table.resizeColumnsToContents()
        self.stat_window.clients_statistics_table.resizeRowsToContents()
        self.stat_window.show()

    def show_server_config(self):
        self.config_window = ServerConfigWindow()
        self.config_window.db_path.insert(self.config['SETTINGS']['Database_path'])
        self.config_window.db_file.insert(self.config['SETTINGS']['Database_file'])
        self.config_window.port.insert(self.config['SETTINGS']['Default_port'])
        self.config_window.ip.insert(self.config['SETTINGS']['Listen_Address'])
        self.config_window.save_button.clicked.connect(self.save_server_config)

    def save_server_config(self):
        global config_window
        message = QMessageBox()
        self.config['SETTINGS']['Database_path'] = config_window.db_path.text()
        self.config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Error', 'Port must be an integer')
        else:
            self.config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                self.config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open(f'{BASE_DIR}/server/server.ini', 'w') as conf:
                    self.config.write(conf)
                    message.information(
                        config_window, 'Ok', 'Settings saved')
            else:
                message.warning(
                    config_window,
                    'Error',
                    'port number must be a number between 1024 and 65536')

    def update_active_users(self):
        self.ui.active_clients_table.setModel(self.gui_create_active_users_table(self.db))
        self.ui.active_clients_table.resizeColumnsToContents()
        self.ui.active_clients_table.resizeRowsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from server.server_database import ServerDB

    config = configparser.ConfigParser()
    config_path = os.path.join(BASE_DIR, 'server', 'server_test.ini')
    config.read(config_path)

    config.add_section('SETTINGS')
    config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
    config.set('SETTINGS', 'Listen_Address', LISTEN_ADDRESS)
    config.set('SETTINGS', 'Database_path', '')
    config.set('SETTINGS', 'Database_file', 'server_test_db')
    database_path = os.path.join(
        config['SETTINGS']['Database_path'],
        config['SETTINGS']['Database_file'])
    database = ServerDB(database_path)

    window = ServerMainWindow(config, database)
    sys.exit(app.exec_())
