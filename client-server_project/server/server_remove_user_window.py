from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class DelUserDialog(QDialog):
    '''
    Класс - диалог выбора контакта для удаления.
    '''

    def __init__(self, database, server):
        super().__init__()
        self.database = database
        self.server = server

        self.setFixedSize(350, 120)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel(
            'Выберите пользователя для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)
        self.btn_ok.clicked.connect(self.remove_user)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.all_users_fill()

    def all_users_fill(self):
        self.selector.addItems([item[0] for item in self.database.get_all_users()])

    def remove_user(self):
        '''Метод - обработчик удаления пользователя.'''
        self.database.remove_user(self.selector.currentText())
        if self.selector.currentText() in self.server.client_usernames:
            sock = self.server.client_usernames[self.selector.currentText()]
            del self.server.client_usernames[self.selector.currentText()]
            self.server.client_logout(sock)
        self.server.send_service_update_message()
        self.close()
