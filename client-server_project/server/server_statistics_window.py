import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QPushButton, QTableView, QApplication


class ServerStatisticsWindow(QDialog):
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ServerStatisticsWindow()
    test_list = QStandardItemModel(window)
    test_list.setHorizontalHeaderLabels(
        ['Username', 'Last connection time', 'Messages sent', 'Messages received'])
    test_list.appendRow(
        [QStandardItem('test1'), QStandardItem('Fri Dec 12 16:20:34 2020'), QStandardItem('2'), QStandardItem('3')])
    test_list.appendRow(
        [QStandardItem('test2'), QStandardItem('Fri Dec 12 16:23:12 2020'), QStandardItem('8'), QStandardItem('5')])
    window.clients_statistics_table.setModel(test_list)
    window.clients_statistics_table.resizeColumnsToContents()

    sys.exit(app.exec_())
