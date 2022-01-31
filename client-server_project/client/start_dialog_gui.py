# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'start_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtWidgets


class UI_StartDialog(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(300, 100)
        self.main_layout = QtWidgets.QGridLayout(Form)
        self.main_layout.setObjectName("main_layout")
        self.layout_username = QtWidgets.QHBoxLayout()
        self.layout_username.setObjectName("layout_username")
        self.label_username = QtWidgets.QLabel(Form)
        self.label_username.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_username.setObjectName("label_username")
        self.layout_username.addWidget(self.label_username)
        self.input_username = QtWidgets.QLineEdit(Form)
        self.input_username.setObjectName("input_username")
        self.layout_username.addWidget(self.input_username)
        self.main_layout.addLayout(self.layout_username, 0, 0, 1, 1)
        self.layout_buttons = QtWidgets.QHBoxLayout()
        self.layout_buttons.setObjectName("layout_buttons")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.layout_buttons.addItem(spacerItem)
        self.button_ok = QtWidgets.QPushButton(Form)
        self.button_ok.setObjectName("button_ok")
        self.layout_buttons.addWidget(self.button_ok)
        self.button_cancel = QtWidgets.QPushButton(Form)
        self.button_cancel.setObjectName("button_cancel")
        self.layout_buttons.addWidget(self.button_cancel)
        self.main_layout.addLayout(self.layout_buttons, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_username.setText(_translate("Form", "Username:"))
        self.button_ok.setText(_translate("Form", "Ok"))
        self.button_cancel.setText(_translate("Form", "Cancel"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = UI_StartDialog()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
