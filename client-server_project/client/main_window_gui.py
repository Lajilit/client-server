# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import os

from PyQt5 import QtCore, QtGui, QtWidgets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)
        MainWindow.setMaximumSize(QtCore.QSize(2000, 2000))

        self.main_widget = QtWidgets.QWidget(MainWindow)
        self.main_widget.setObjectName("main_widget")

        self.layout_main_widget = QtWidgets.QGridLayout(self.main_widget)
        self.layout_main_widget.setObjectName("layout_main_widget")

        self.layout_contacts = QtWidgets.QVBoxLayout()
        self.layout_contacts.setObjectName("layout_contacts")

        self.layout_search = QtWidgets.QHBoxLayout()
        self.layout_search.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.layout_search.setSpacing(0)
        self.layout_search.setObjectName("layout_search")

        self.label_search = QtWidgets.QLabel(self.main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_search.sizePolicy().hasHeightForWidth())
        self.label_search.setSizePolicy(sizePolicy)
        self.label_search.setMinimumSize(QtCore.QSize(30, 30))
        self.label_search.setMaximumSize(QtCore.QSize(30, 30))
        self.label_search.setText("")
        self.label_search.setPixmap(QtGui.QPixmap(os.path.join(BASE_DIR, 'client', 'img', 'search.png')))
        self.label_search.setObjectName("label_search")

        self.layout_search.addWidget(self.label_search)

        self.input_search = QtWidgets.QTextEdit(self.main_widget)
        self.input_search.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_search.sizePolicy().hasHeightForWidth())
        self.input_search.setSizePolicy(sizePolicy)
        self.input_search.setMinimumSize(QtCore.QSize(0, 0))
        self.input_search.setMaximumSize(QtCore.QSize(170, 30))
        self.input_search.setObjectName("input_search")

        self.layout_search.addWidget(self.input_search)

        self.layout_contacts.addLayout(self.layout_search)

        self.list_contacts = QtWidgets.QListView(self.main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_contacts.sizePolicy().hasHeightForWidth())
        self.list_contacts.setSizePolicy(sizePolicy)
        self.list_contacts.setMinimumSize(QtCore.QSize(200, 500))
        self.list_contacts.setMaximumSize(QtCore.QSize(200, 2000))
        self.list_contacts.setSizeIncrement(QtCore.QSize(0, 0))
        self.list_contacts.setObjectName("list_contacts")

        self.layout_contacts.addWidget(self.list_contacts)

        self.button_add_contact = QtWidgets.QPushButton(self.main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_add_contact.sizePolicy().hasHeightForWidth())
        self.button_add_contact.setSizePolicy(sizePolicy)
        self.button_add_contact.setMaximumSize(QtCore.QSize(200, 30))
        self.button_add_contact.setObjectName("button_add_contact")

        self.layout_contacts.addWidget(self.button_add_contact)

        self.layout_main_widget.addLayout(self.layout_contacts, 0, 0, 1, 1)

        self.layout_messages = QtWidgets.QVBoxLayout()
        self.layout_messages.setObjectName("messages")

        self.layout_contact_name = QtWidgets.QHBoxLayout()
        self.layout_contact_name.setObjectName("layout_contact_name")

        self.label_contact_name = QtWidgets.QLabel(self.main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_contact_name.sizePolicy().hasHeightForWidth())
        self.label_contact_name.setSizePolicy(sizePolicy)
        self.label_contact_name.setMinimumSize(QtCore.QSize(0, 30))
        self.label_contact_name.setObjectName("label_contact_name")

        self.layout_contact_name.addWidget(self.label_contact_name)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_contact_name.addItem(spacerItem)

        self.button_remove_contact = QtWidgets.QPushButton(self.main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_remove_contact.sizePolicy().hasHeightForWidth())
        self.button_remove_contact.setSizePolicy(sizePolicy)
        self.button_remove_contact.setMaximumSize(QtCore.QSize(200, 30))
        self.button_remove_contact.setObjectName("button_remove_contact")

        self.layout_contact_name.addWidget(self.button_remove_contact)

        self.layout_messages.addLayout(self.layout_contact_name)

        self.list_messages = QtWidgets.QListView(self.main_widget)
        self.list_messages.setMinimumSize(QtCore.QSize(500, 400))
        self.list_messages.setMaximumSize(QtCore.QSize(2000, 2000))
        self.list_messages.setObjectName("list_messages")

        self.layout_messages.addWidget(self.list_messages)

        self.input_new_message = QtWidgets.QTextEdit(self.main_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(self.input_new_message.sizePolicy().hasHeightForWidth())
        self.input_new_message.setSizePolicy(sizePolicy)
        self.input_new_message.setMinimumSize(QtCore.QSize(500, 100))
        self.input_new_message.setMaximumSize(QtCore.QSize(2000, 100))
        self.input_new_message.setObjectName("input_new_message")

        self.layout_messages.addWidget(self.input_new_message)

        self.layout_send_message = QtWidgets.QHBoxLayout()
        self.layout_send_message.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.layout_send_message.setObjectName("layout_send_message")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_send_message.addItem(spacerItem)

        self.button_send_message = QtWidgets.QPushButton(self.main_widget)
        self.button_send_message.setObjectName("button_send_message")

        self.layout_send_message.addWidget(self.button_send_message)

        self.layout_messages.addLayout(self.layout_send_message)

        self.layout_main_widget.addLayout(self.layout_messages, 0, 1, 1, 1)

        MainWindow.setCentralWidget(self.main_widget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 964, 22))
        self.menubar.setObjectName("menubar")
        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_contacts = QtWidgets.QMenu(self.menubar)
        self.menu_contacts.setObjectName("menu_contacts")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.action_exit = QtWidgets.QAction(MainWindow)
        self.action_exit.setObjectName("action_exit")
        self.action_add_contact = QtWidgets.QAction(MainWindow)
        self.action_add_contact.setObjectName("action_add_contact")
        self.action_remove_contact = QtWidgets.QAction(MainWindow)
        self.action_remove_contact.setObjectName("action_remove_contact")

        self.menu_file.addAction(self.action_exit)
        self.menu_contacts.addAction(self.action_add_contact)
        self.menu_contacts.addAction(self.action_remove_contact)
        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_contacts.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Messenger Application"))
        self.input_search.setHtml(_translate(
            "MainWindow",
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"
        ))
        self.button_add_contact.setText(_translate("MainWindow", "Add new contact"))
        self.label_contact_name.setText(_translate("MainWindow", "Choose contact to show history"))
        self.button_remove_contact.setText(_translate("MainWindow", "Remove Contact"))
        self.button_send_message.setText(_translate("MainWindow", "Send message"))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.menu_contacts.setTitle(_translate("MainWindow", "Contacts"))
        self.action_exit.setText(_translate("MainWindow", "Exit"))
        self.action_add_contact.setText(_translate("MainWindow", "Add contact"))
        self.action_remove_contact.setText(_translate("MainWindow", "Remove contact"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
