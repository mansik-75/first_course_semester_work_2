from PyQt6.QtGui import QColor, QPolygon

from win_py import edit, game, start
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import QtWidgets, QtGui
import socket
import threading


class MainDrawer:
    @staticmethod
    def draw_grid(view, scene: QtWidgets.QGraphicsScene):

        view.setScene(scene)

        for i in range(40, 361, 40):
            scene.addLine(0, i, 397, i)
            scene.addLine(i, 0, i, 397)

    @staticmethod
    def draw_ships(scene: QtWidgets.QGraphicsScene):
        for i in range(0, 361, 40):
            scene.addRect(i, i, 40, 40, QColor(183, 117, 117))


class EditWin(QMainWindow, edit.Ui_MainWindow, MainDrawer):
    """Класс, который отвечает за работу окна расстановки кораблей"""
    def __init__(self, username):
        super(EditWin, self).__init__()
        self.setupUi(self)
        self.username = username
        self.ships = [[0 for _ in range(12)] for _ in range(12)]
        self.ships_count = [4, 3, 2, 1]
        self.ship_type = 1
        self.radioButton.setChecked(True)
        self.orientation = 'g'
        self.radioButton_5.setChecked(True)

        self.pushButton.clicked.connect(lambda x: print(self.username))
        self.pushButton_2.clicked.connect(self.go_to_game_page)

        self.radioButton.clicked.connect(lambda: self.set_ship_type(1))
        self.radioButton_2.clicked.connect(lambda: self.set_ship_type(2))
        self.radioButton_3.clicked.connect(lambda: self.set_ship_type(3))
        self.radioButton_4.clicked.connect(lambda: self.set_ship_type(4))
        self.radioButton_5.clicked.connect(lambda: self.set_orientation('g'))
        self.radioButton_6.clicked.connect(lambda: self.set_orientation('v'))

        self.edit_scene = QtWidgets.QGraphicsScene()
        self.draw_grid(self.graphicsView, self.edit_scene)

        self.setWindowTitle(f'Привет, {self.username}!')

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        position = a0.pos()
        item_pos = self.graphicsView.mapFrom(self, position)
        x, y = item_pos.x()//40+1, item_pos.y()//40+1
        print(x, y)
        if 0 < x < 11 and 0 < y < 11:
            self.set_ship(x, y)

    def set_orientation(self, orientation):
        self.orientation = orientation

    def set_ship_type(self, ship_type):
        self.ship_type = ship_type
        print(self.ship_type)

    def set_ship(self, x, y):
        check = self.check_position(y, x)
        if check:
            if self.orientation == 'v':
                for i in range(x, x + self.ship_type):
                    self.ships[i][y] = 1
                    self.ships[i][y - 1] = self.ships[i][y + 1] = 2
                self.ships[x - 1][y - 1] = self.ships[x - 1][y] = self.ships[x - 1][y + 1] = 2
                self.ships[x + self.ship_type][y - 1] = self.ships[x + self.ship_type][y] = self.ships[x + self.ship_type][y + 1] = 2
            if self.orientation == 'g':
                for i in range(y, y + self.ship_type):
                    self.ships[x][i] = 1
                    self.ships[x - 1][i] = self.ships[x + 1][i] = 2
                self.ships[x - 1][y - 1] = self.ships[x][y - 1] = self.ships[x + 1][y - 1] = 2
                self.ships[x - 1][y + self.ship_type] = self.ships[x][y + self.ship_type] = self.ships[x + 1][y + self.ship_type] = 2
        for i in self.ships:
            print(*i)
        for i in range(1, 11):
            for j in range(1, 11):
                if self.ships[j][i] == 1:
                    print('ye')
                    self.edit_scene.addRect((j-1)*40, (i-1)*40, 40, 40, brush=QColor(183, 117, 117))

    def set_battleship(self):
        """Линкор 4 клетки"""
        pass

    def set_cruiser(self):
        """Крейсер 3 клетки"""
        pass

    def set_destroyer(self):
        """Эсминец 2 клетки"""
        pass

    def set_cutter(self):
        """Катер 1 клетка"""
        pass

    def go_to_game_page(self):
        self.game_page = GameWin(self.username)
        self.game_page.show()
        self.close()

    def check_position(self, x, y):
        if self.orientation == 'v':
            if x + self.ship_type > 11:
                return False
            for i in range(x, x + self.ship_type):
                if i == x:
                    if self.ships[i - 1][y] == 1 or self.ships[i - 1][y - 1] == 1 or self.ships[i - 1][y + 1] == 1:
                        return False
                if i == (x + self.ship_type - 1):
                    if self.ships[i + 1][y] == 1 or self.ships[i + 1][y - 1] == 1 or self.ships[i + 1][y + 1] == 1:
                        return False
                if self.ships[i][y] in {1, 2}:
                    return False
                if self.ships[i][y - 1] == 1 or self.ships[i][y + 1] == 1:
                    return False
            return True
        if self.orientation == 'g':
            if y + self.ship_type > 11:
                return False
            for i in range(y, y + self.ship_type):
                if i == y:
                    if self.ships[x - 1][i - 1] == 1 or self.ships[x][i - 1] == 1 or self.ships[x + 1][i - 1] == 1:
                        return False
                if i == (y + self.ship_type - 1):
                    if self.ships[x - 1][i + 1] == 1 or self.ships[x][i + 1] == 1 or self.ships[x + 1][i + 1] == 1:
                        return False
                if self.ships[x][i] in {1, 2}:
                    return False
                if self.ships[x - 1][i] == 1 or self.ships[x + 1][i] == 1:
                    return False
            return True


class GameWin(QMainWindow, game.Ui_MainWindow, MainDrawer):
    """Класс, который отвечает за окно игры"""
    def __init__(self, username):
        super(GameWin, self).__init__()
        self.setupUi(self)
        self.username = username

        self.scene_main = QtWidgets.QGraphicsScene()
        self.scene_en = QtWidgets.QGraphicsScene()

        self.draw_grid(self.graphicsView, self.scene_main)
        self.draw_grid(self.graphicsView_2, self.scene_en)


class StartWin(QMainWindow, start.Ui_MainWindow):
    """Класс, который отвечает за окно с вписыванием юзернейма"""
    def __init__(self):
        super(StartWin, self).__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.go_to_edit_page)

    def go_to_edit_page(self):
        username = self.lineEdit.text()
        if not username:
            return
        self.edit_page = EditWin(username)
        self.edit_page.show()
        self.close()


if __name__ == '__main__':

    app = QApplication([])
    window = StartWin()
    window.show()
    app.exec()

