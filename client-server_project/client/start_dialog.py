from PyQt5.QtWidgets import QDialog, QApplication, qApp

from client.start_dialog_ui import UI_StartDialog


class StartDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = UI_StartDialog()
        self.ui.setupUi(self)
        self.ok_pressed = False

        self.setWindowTitle('Hello!')
        print(self.ui.__dict__)
        self.ui.button_ok.clicked.connect(self.click)
        self.ui.button_cancel.clicked.connect(qApp.exit)

        self.show()

    def click(self):
        if self.ui.input_username.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = StartDialog()
    app.exec_()
