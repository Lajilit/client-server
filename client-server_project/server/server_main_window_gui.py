# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'server_main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import qApp

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)


class Server_Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setWindowTitle('Server administration panel')
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(5, 5, 106, 20))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")

        self.active_clients_table = QtWidgets.QTableView(self.centralwidget)
        self.active_clients_table.setGeometry(QtCore.QRect(5, 30, 790, 500))
        self.active_clients_table.setObjectName("active_clients_table")
        MainWindow.setCentralWidget(self.centralwidget)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.refresh_users_list_button = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon(os.path.join(BASE_DIR, 'server', 'img', 'refresh_btn.png'))
        self.refresh_users_list_button.setIcon(icon)
        self.refresh_users_list_button.setObjectName("refresh_users_list_button")

        self.show_clients_statistics_button = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon(os.path.join(BASE_DIR, 'server', 'img', 'message_history_btn.png'))
        self.show_clients_statistics_button.setIcon(icon1)
        self.show_clients_statistics_button.setObjectName("show_clients_statistics_button")

        self.show_server_configuration_button = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon(os.path.join(BASE_DIR, 'server', 'img', 'config_btn.png'))
        self.show_server_configuration_button.setIcon(icon2)
        self.show_server_configuration_button.setObjectName("show_server_configuration_button")

        self.add_user_button = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon(os.path.join(BASE_DIR, 'server', 'img', 'add_user_button.png'))
        self.add_user_button.setIcon(icon)
        self.add_user_button.setObjectName("add_user_button")

        self.remove_user_button = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon(os.path.join(BASE_DIR, 'server', 'img', 'remove_user_button.png'))
        self.remove_user_button.setIcon(icon)
        self.remove_user_button.setObjectName("remove_user_button")

        self.exit_action = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon(os.path.join(BASE_DIR, 'server', 'img', 'exit_btn.png'))
        self.exit_action.setIcon(icon3)
        self.exit_action.setObjectName("exit_action")


        self.toolBar.addAction(self.refresh_users_list_button)
        self.toolBar.addAction(self.show_clients_statistics_button)
        self.toolBar.addAction(self.show_server_configuration_button)
        self.toolBar.addAction(self.add_user_button)
        self.toolBar.addAction(self.remove_user_button)
        self.toolBar.addAction(self.exit_action)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Active users list"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.refresh_users_list_button.setText(_translate("MainWindow", "Обновить список"))
        self.refresh_users_list_button.setToolTip(_translate("MainWindow", "обновить список активных пользователей"))
        self.show_clients_statistics_button.setText(_translate("MainWindow", "Статистика клиентов"))
        self.show_clients_statistics_button.setToolTip(_translate("MainWindow", "Показать статистику сообщений клиентов"))
        self.add_user_button.setToolTip(_translate("MainWindow", "Добавить пользователя"))
        self.remove_user_button.setToolTip(_translate("MainWindow", "Удалить пользователя"))
        self.show_server_configuration_button.setText(_translate("MainWindow", "Настройки"))
        self.show_server_configuration_button.setToolTip(_translate("MainWindow", "Открыть конфигурацию сервера"))
        self.exit_action.setText(_translate("MainWindow", "Выход"))
        self.exit_action.setToolTip(_translate("MainWindow", "Выход"))
