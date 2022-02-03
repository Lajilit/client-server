import os
import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, QTableView, QDialog, QPushButton, \
    QLineEdit, QFileDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

def gui_create_active_users_table(database):
    active_users = database.get_active_users()
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


def gui_create_clients_statistics_table(database):
    clients_statistics = database.get_client_statistics()

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


class ServerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        exit_action = QAction(QIcon(os.path.join(BASE_DIR, 'server', 'img', 'exit_btn.png')), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)

        self.refresh_users_list_button = QAction(
            QIcon(os.path.join(BASE_DIR, 'server', 'img', 'refresh_btn.png')), 'Refresh active users list', self)

        self.show_server_configuration_button = QAction(
            QIcon(os.path.join(BASE_DIR, 'server', 'img', 'config_btn.png')), 'Server configuration', self)

        self.show_clients_statistics_button = QAction(
            QIcon(os.path.join(BASE_DIR, 'server', 'img', 'message_history_btn.png')), 'Messages history', self)

        self.statusBar()

        self.toolbar = self.addToolBar('MainToolBar')
        self.toolbar.addAction(self.refresh_users_list_button)
        self.toolbar.addAction(self.show_clients_statistics_button)
        self.toolbar.addAction(self.show_server_configuration_button)
        self.toolbar.addAction(exit_action)

        self.setFixedSize(800, 600)
        self.setWindowTitle('Server administration panel')

        self.label = QLabel('Active users list', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 40)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 60)
        self.active_clients_table.setFixedSize(780, 400)

        self.show()


class ClientStatisticsWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Clients statistics')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Close', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.clients_statistics_table = QTableView(self)
        self.clients_statistics_table.move(10, 10)
        self.clients_statistics_table.setFixedSize(580, 620)

        self.show()


class ServerConfigWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setFixedSize(365, 260)
        self.setWindowTitle('Server configuration')

        self.db_path_label = QLabel('Database path: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.select_db_button = QPushButton('Find...', self)
        self.select_db_button.move(275, 28)

        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.select_db_button.clicked.connect(open_file_dialog)

        self.db_file_label = QLabel('Database: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Port: ', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('IP address:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel(' leave this field empty\n to accept connections from any IP address.', self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(190, 220)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = ServerMainWindow()
    main_window.statusBar().showMessage('Test Statusbar Message')
    test_list = QStandardItemModel(main_window)
    test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    test_list.appendRow(
        [QStandardItem('test1'), QStandardItem('192.198.0.5'), QStandardItem('23544'), QStandardItem('16:20:34')])
    test_list.appendRow(
        [QStandardItem('test2'), QStandardItem('192.198.0.8'), QStandardItem('33245'), QStandardItem('16:22:11')])
    main_window.active_clients_table.setModel(test_list)
    main_window.active_clients_table.resizeColumnsToContents()
    app.exec_()

    # ----------------------------------------------------------
    # app = QApplication(sys.argv)
    # dial = ConfigWindow()
    #
    # app.exec_()

    # ----------------------------------------------------------
    # app = QApplication(sys.argv)
    # window = ClientStatisticsWindow()
    # test_list = QStandardItemModel(window)
    # test_list.setHorizontalHeaderLabels(
    #     ['Username', 'Last connection time', 'Messages sent', 'Messages received'])
    # test_list.appendRow(
    #     [QStandardItem('test1'), QStandardItem('Fri Dec 12 16:20:34 2020'), QStandardItem('2'), QStandardItem('3')])
    # test_list.appendRow(
    #     [QStandardItem('test2'), QStandardItem('Fri Dec 12 16:23:12 2020'), QStandardItem('8'), QStandardItem('5')])
    # window.clients_statistics_table.setModel(test_list)
    # window.clients_statistics_table.resizeColumnsToContents()
    #
    # app.exec_()
