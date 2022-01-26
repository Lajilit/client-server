import os
import sys

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_logging.config.log_config import client_logger as logger


class AddContactDialog(QDialog):
    def __init__(self, server_int, db):
        super().__init__()
        self.server_interaction = server_int
        self.database = db

        self.setFixedSize(350, 120)
        self.setWindowTitle('Add contact')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Select user to add new contact', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.button_refresh = QPushButton('Refresh users list', self)
        self.button_refresh.setFixedSize(100, 30)
        self.button_refresh.move(60, 60)

        self.button_add = QPushButton('Add', self)
        self.button_add.setFixedSize(100, 30)
        self.button_add.move(230, 20)

        self.button_cancel = QPushButton('Cancel', self)
        self.button_cancel.setFixedSize(100, 30)
        self.button_cancel.move(230, 60)
        self.button_cancel.clicked.connect(self.close)

        self.get_users_to_select_from_db()

        self.button_refresh.clicked.connect(self.update_users_to_select_from_server)

    def get_users_to_select_from_db(self):
        self.selector.clear()

        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_known_users())

        users_list.remove(self.server_interaction.name)
        self.selector.addItems(users_list - contacts_list)

    def update_users_to_select_from_server(self):
        try:
            self.server_interaction.load_data()
        except OSError:
            pass
        else:
            logger.debug('Users list updated')
            self.get_users_to_select_from_db()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from client_database import ClientDB
    database = ClientDB('test3')
    from server_interaction import ClientServerInteraction
    transport = ClientServerInteraction('127.0.0.1', 7777, 'test3', database)
    window = AddContactDialog(transport, database)
    window.show()
    app.exec_()
