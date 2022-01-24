import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, qApp, QApplication, QMessageBox

from client.add_contact_dialog import AddContactDialog
from client.main_window_gui import Ui_MainWindow
from errors import ServerError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from project_logging.config.log_config import client_logger as logger

class ClientMainWindow(QMainWindow):
    def __init__(self, database, server_interaction):
        super().__init__()
        self.database = database
        self.server_interaction = server_interaction

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.action_exit.triggered.connect(qApp.exit)

        # self.ui.button_send_message.clicked.connect(self.send_message)

        self.ui.button_add_contact.clicked.connect(self.add_contact_window)
        self.ui.action_add_contact.triggered.connect(self.add_contact_window)
        #
        # self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        # self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        # Дополнительные требующиеся атрибуты
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_contact = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        self.ui.list_contacts.clicked.connect(self.set_current_contact)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        self.ui.label_contact_name.setText("Choose contact from contacts list")
        self.ui.input_new_message.clear()
        if self.history_model:
            self.history_model.clear()

        self.ui.button_send_message.setDisabled(True)
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

    def set_current_contact(self):
        self.current_contact = self.ui.list_contacts.currentIndex().data()

        self.ui.label_contact_name.setText(f'{self.current_contact}:')
        self.ui.button_send_message.setDisabled(False)
        self.ui.input_new_message.setDisabled(False)

        # Заполняем окно историю сообщений по требуемому пользователю.
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
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        try:
            self.server_interaction.add_contact(new_contact)
        except OSError as e:
            if e.errno:
                self.messages.critical(self, 'Error', 'Server connection lost')
                self.close()
            self.messages.critical(self, 'Error', 'Connection timeout')
        else:
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            self.messages.information(self, 'Success', f'Contact {new_contact} added successfully')
    #
    # # Функция удаления контакта
    # def delete_contact_window(self):
    #     global remove_dialog
    #     remove_dialog = DelContactDialog(self.database)
    #     remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
    #     remove_dialog.show()
    #
    # # Функция обработчик удаления контакта, сообщает на сервер, обновляет таблицу контактов
    # def delete_contact(self, item):
    #     selected = item.selector.currentText()
    #     try:
    #         self.transport.remove_contact(selected)
    #     except ServerError as err:
    #         self.messages.critical(self, 'Ошибка сервера', err.text)
    #     except OSError as err:
    #         if err.errno:
    #             self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
    #             self.close()
    #         self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
    #     else:
    #         self.database.del_contact(selected)
    #         self.clients_list_update()
    #         logger.info(f'Успешно удалён контакт {selected}')
    #         self.messages.information(self, 'Успех', 'Контакт успешно удалён.')
    #         item.close()
    #         # Если удалён активный пользователь, то деактивируем поля ввода.
    #         if selected == self.current_contact:
    #             self.current_contact = None
    #             self.set_disabled_input()

    # def send_message(self):
    #     message_text = self.ui.input_new_message.toPlainText()
    #     if message_text:
    #         try:
    #             self.server_interaction.send_message(self.current_contact, message_text)
    #             pass
    #         except ServerError as err:
    #             self.messages.critical(self, 'Ошибка', err.text)
    #         except OSError as err:
    #             if err.errno:
    #                 self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
    #                 self.close()
    #             self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
    #         except (ConnectionResetError, ConnectionAbortedError):
    #             self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
    #             self.close()
    #         else:
    #             self.database.save_message(self.current_contact, 'out', message_text)
    #             logger.debug(f'Отправлено сообщение для {self.current_contact}: {message_text}')
    #             self.update_message_history()
    #     self.ui.input_new_message.clear()
    #
    # # Слот приёма нового сообщений
    # @pyqtSlot(str)
    # def message(self, sender):
    #     if sender == self.current_chat:
    #         self.history_list_update()
    #     else:
    #         # Проверим есть ли такой пользователь у нас в контактах:
    #         if self.database.check_contact(sender):
    #             # Если есть, спрашиваем и желании открыть с ним чат и открываем при желании
    #             if self.messages.question(self, 'Новое сообщение', \
    #                                       f'Получено новое сообщение от {sender}, открыть чат с ним?', QMessageBox.Yes,
    #                                       QMessageBox.No) == QMessageBox.Yes:
    #                 self.current_chat = sender
    #                 self.set_active_user()
    #         else:
    #             print('NO')
    #             # Раз нет, спрашиваем хотим ли добавить юзера в контакты.
    #             if self.messages.question(self, 'Новое сообщение',
    #                                       f'Получено новое сообщение от {sender}.\n '
    #                                       f'Данного пользователя нет в вашем контакт-листе.\n'
    #                                       f' Добавить в контакты и открыть чат с ним?',
    #                                       QMessageBox.Yes,
    #                                       QMessageBox.No) == QMessageBox.Yes:
    #                 self.add_contact(sender)
    #                 self.current_chat = sender
    #                 self.set_active_user()
    #
    # # Слот потери соединения
    # # Выдаёт сообщение об ошибке и завершает работу приложения
    # @pyqtSlot()
    # def connection_lost(self):
    #     self.messages.warning(self, 'Сбой соединения', 'Потеряно соединение с сервером. ')
    #     self.close()
    #
    # def make_connection(self, trans_obj):
    #     trans_obj.new_message.connect(self.message)
    #     trans_obj.connection_lost.connect(self.connection_lost)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from client_database import ClientDB

    database = ClientDB('test3')
    from client_server_interaction import ClientServerInteraction

    transport = ClientServerInteraction('127.0.0.1', 7777, 'test3', database)
    window = ClientMainWindow(database, transport)
    sys.exit(app.exec_())
