import json
import os
import sys

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, qApp, QApplication, QMessageBox

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from client.add_contact_dialog import AddContactDialog
from client.main_window_gui import Ui_MainWindow
from client.remove_contact_dialog import RemoveContactDialog
from common.errors import ServerError



class ClientMainWindow(QMainWindow):
    def __init__(self, db, server_interaction):
        super().__init__()
        self.database = db
        self.server_interaction = server_interaction

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.action_exit.triggered.connect(qApp.exit)

        self.ui.button_send_message.clicked.connect(self.send_message)

        self.ui.button_add_contact.clicked.connect(self.add_contact_window)
        self.ui.action_add_contact.triggered.connect(self.add_contact_window)

        self.ui.button_remove_contact.clicked.connect(self.remove_contact)
        self.ui.action_remove_contact.triggered.connect(self.remove_contact_window)

        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_contact = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        self.ui.list_contacts.clicked.connect(self.select_contact)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        self.ui.label_contact_name.setText("Choose contact from contacts list")
        self.ui.input_new_message.clear()
        if self.history_model:
            self.history_model.clear()

        self.ui.button_send_message.setDisabled(True)
        self.ui.button_remove_contact.setDisabled(True)
        self.ui.input_new_message.setDisabled(True)

    def update_message_history(self):

        message_history = sorted(self.database.get_user_message_history(self.server_interaction.name,
                                                                        self.current_contact),
                                 key=lambda msg: msg[3])

        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)

        self.history_model.clear()

        length = len(message_history)
        start_index = 0
        if length > 20:
            start_index = length - 20

        for i in range(start_index, length):
            item = message_history[i]
            if item[1] == self.server_interaction.name:
                message = QStandardItem(f'{item[3].replace(microsecond=0)}\n {item[2]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(255, 213, 213)))
                message.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(message)
            else:
                message = QStandardItem(f'{item[3].replace(microsecond=0)}\n {item[2]}')
                message.setEditable(False)
                message.setTextAlignment(Qt.AlignRight)
                message.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(message)
        self.ui.list_messages.scrollToBottom()

    def select_contact(self):
        self.current_contact = self.ui.list_contacts.currentIndex().data()
        self.set_current_contact()

    def set_current_contact(self):
        self.ui.label_contact_name.setText(f'{self.current_contact}:')
        self.ui.button_send_message.setDisabled(False)
        self.ui.input_new_message.setDisabled(False)
        self.ui.button_remove_contact.setDisabled(False)

        self.update_message_history()

    def clients_list_update(self):
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContactDialog(self.server_interaction, self.database)
        select_dialog.button_add.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        new_contact_name = item.selector.currentText()
        self.add_contact(new_contact_name)
        item.close()

    def add_contact(self, new_contact_name):
        try:
            self.server_interaction.add_contact(new_contact_name)
        except OSError as e:
            if e.errno:
                self.messages.critical(self, 'Error', 'Server connection lost')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
            self.messages.critical(self, 'Error', 'Server connection lost')
            self.close()
        else:
            new_contact = QStandardItem(new_contact_name)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            self.messages.information(self, 'Success', f'Contact {new_contact_name} added successfully')

    def remove_contact_window(self):
        global remove_dialog
        remove_dialog = RemoveContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(lambda: self.remove_contact(remove_dialog))
        remove_dialog.show()

    def remove_contact_action(self, item):
        contact_to_remove = item.selector.currentText()
        self.remove_contact(contact_to_remove)
        item.close()

    def remove_contact(self, contact_to_remove=None):
        if not contact_to_remove:
            contact_to_remove = self.current_contact
        try:
            self.server_interaction.remove_contact(contact_to_remove)
        except OSError as e:
            if e.errno:
                self.messages.critical(self, 'Error', 'Server connection lost')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
            self.messages.critical(self, 'Error', 'Server connection lost')
            self.close()
        else:
            self.database.remove_contact(contact_to_remove)
            self.clients_list_update()

            self.messages.information(self, 'Success', f'Contact {contact_to_remove} removed successfully')
            if contact_to_remove == self.current_contact:
                self.current_contact = None
                self.set_disabled_input()

    def send_message(self):
        message_text = self.ui.input_new_message.toPlainText()
        if message_text:
            try:
                result = self.server_interaction.send_message(self.current_contact, message_text)
                pass
            except ServerError as e:
                self.messages.critical(self, 'Error', e.error_text)
            except OSError as e:
                if e.errno:
                    self.messages.critical(self, 'Error', 'Server connection lost')
                    self.close()
                self.messages.critical(self, 'Error', 'Connection timeout')
            except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                self.messages.critical(self, 'Error', 'Server connection lost')
                self.close()
            else:
                if result == 'ok':
                    self.database.save_message(self.server_interaction.name, self.current_contact, message_text)
                    self.update_message_history()
                else:
                    self.messages.warning(self, 'Error', result)

        self.ui.input_new_message.clear()

    @pyqtSlot(str)
    def message(self, sender):
        if sender == self.current_contact:
            self.update_message_history()
        else:
            if self.database.check_user_is_a_contact(sender):
                if self.messages.question(self,
                                          'New message',
                                          f'Received new message from {sender}, do you want to start messaging?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_contact = sender
                    self.set_current_contact()
            else:
                if self.messages.question(self,
                                          'New message',
                                          f'Received new message from {sender}.\n '
                                          f'Do you want to add him to your contacts and start messaging?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_contact = sender
                    self.set_current_contact()

    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, 'Connection failure', 'Server connection lost')
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from client.client_database import ClientDB

    database = ClientDB('test30')
    from server_interaction import ClientServerInteraction

    server_int = ClientServerInteraction('127.0.0.1', 7777, 'test30', database)
    window = ClientMainWindow(database, server_int)
    sys.exit(app.exec_())
