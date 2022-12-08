from win_py import edit, game, start
from PyQt6.QtWidgets import QMainWindow, QApplication
import socket
import threading


class EditWin(QMainWindow, edit.Ui_MainWindow):

    def __init__(self):
        super(EditWin, self).__init__()
        self.setupUi(self)
        

class GameWin(QMainWindow, game.Ui_MainWindow):

    def __init__(self):
        super(GameWin, self).__init__()
        self.setupUi(self)


class StartWin(QMainWindow, start.Ui_MainWindow):

    def __init__(self):
        super(StartWin, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':

    app = QApplication([])
    window = EditWin()
    window.show()
    app.exec()

