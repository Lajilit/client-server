from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, QMessageBox, qApp
from PyQt5.QtCore import Qt
import hashlib
import binascii

from server.server_user_registration_gialog_gui import UI_UserRegisterDialog


class RegisterUserDialog(QDialog):

    def __init__(self, database, server):
        super().__init__()
        self.ui = UI_UserRegisterDialog()
        self.ui.setupUi(self)

        self.database = database
        self.server = server

        self.setWindowTitle('Регистрация')
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.ui.button_ok.clicked.connect(self.save_data)
        self.ui.button_cancel.clicked.connect(self.close)

        self.messages = QMessageBox()

        self.show()

    def save_data(self):
        """
        Метод проверки правильности ввода и сохранения в базу нового пользователя.
        """
        if not self.ui.input_username.text():
            self.messages.critical(
                self, 'Ошибка', 'Не указано имя пользователя.')
            return
        elif self.ui.input_password_1.text() != self.ui.input_password_2.text():
            self.messages.critical(
                self, 'Ошибка', 'Введённые пароли не совпадают.')
            return
        elif self.database.check_user_exists(self.ui.input_username.text()):
            self.messages.critical(
                self, 'Ошибка', 'Пользователь уже существует.')
            return
        else:
            password_bytes = self.ui.input_password_1.text().encode('utf-8')
            salt = self.ui.input_username.text().lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac(
                'sha512', password_bytes, salt, 10000)
            self.database.add_user(
                self.ui.input_username.text(),
                binascii.hexlify(passwd_hash))
            self.messages.information(
                self, 'Успех', 'Пользователь успешно зарегистрирован.')
            self.server.send_service_update_message()
            self.close()


if __name__ == '__main__':
    app = QApplication([])
    from server.server_database import ServerDB
    database = ServerDB('../server_database.db3')
    from server_core import Server
    server = Server('', 7777, database)
    dial = RegisterUserDialog(database, server)
    app.exec_()
