import os
import sys

from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(BASE_DIR)


class RemoveContactDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.database = db

        self.setFixedSize(350, 120)
        self.setWindowTitle('Remove contact')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Select cintact to remove', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Remove', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.selector.addItems(sorted(self.database.get_contacts()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from client.client_database import ClientDB
    database = ClientDB('test30')
    database.add_contact('test1')
    database.add_contact('test6')
    database.add_contact('test10')
    window = RemoveContactDialog(database)
    window.show()
    app.exec_()
