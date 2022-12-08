from win_py import edit, game, start
from PyQt6.QtWidgets import QMainWindow, QApplication
import socket
import threading


class EditWin(QMainWindow, edit.Ui_MainWindow):

    def __init__(self,):
        super(EditWin, self).__init__()
        self.setupUi(self)
        self.username = ''
        self.pushButton.clicked.connect(lambda x: print(self.username))

class GameWin(QMainWindow, game.Ui_MainWindow):

    def __init__(self):
        super(GameWin, self).__init__()
        self.setupUi(self)


class StartWin(QMainWindow, start.Ui_MainWindow):

    def __init__(self):
        super(StartWin, self).__init__()
        self.setupUi(self)
        self.edit_page = EditWin()

        self.pushButton.clicked.connect(self.go_to_edit_page)

    def go_to_edit_page(self):
        username = self.lineEdit.text()
        if not username:
            return
        self.edit_page.username = username
        self.edit_page.show()
        self.close()


if __name__ == '__main__':

    app = QApplication([])
    window = StartWin()
    window.show()
    app.exec()

