from time import sleep

from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor

from win_py import edit, game, start
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import QtWidgets, QtGui
import socket
import pickle
from threading import Thread


class MainDrawer:
    @staticmethod
    def draw_grid(view, scene: QtWidgets.QGraphicsScene):

        view.setScene(scene)

        for i in range(40, 361, 40):
            scene.addLine(0, i, 397, i)
            scene.addLine(i, 0, i, 397)

    def draw_ships(self):
        for i in range(1, 11):
            for j in range(1, 11):
                if self.ships[i][j] == 1:
                    self.user_scene.addRect((j-1)*40+5, (i-1)*40+5, 30, 30, brush=QColor(183, 117, 117))


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

        self.pushButton.clicked.connect(self.delete_all_ships_from_board)  # кнопка очистить
        self.pushButton_2.clicked.connect(self.go_to_game_page)  # кнопка подтвердить
        self.pushButton_2.clicked.connect(self.close)  # кнопка подтвердить

        self.radioButton.clicked.connect(lambda: self.set_ship_type(1))
        self.radioButton_2.clicked.connect(lambda: self.set_ship_type(2))
        self.radioButton_3.clicked.connect(lambda: self.set_ship_type(3))
        self.radioButton_4.clicked.connect(lambda: self.set_ship_type(4))
        self.radioButton_5.clicked.connect(lambda: self.set_orientation('g'))
        self.radioButton_6.clicked.connect(lambda: self.set_orientation('v'))

        self.user_scene = QtWidgets.QGraphicsScene()
        self.draw_grid(self.graphicsView, self.user_scene)

        self.setWindowTitle(f'Привет, {self.username}!')

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        position = a0.pos()
        item_pos = self.graphicsView.mapFrom(self, position)
        x, y = item_pos.x()//40+1, item_pos.y()//40+1
        print(y, x)
        if 0 < x < 11 and 0 < y < 11:
            self.set_ship(y, x)

    def set_orientation(self, orientation):
        self.orientation = orientation

    def set_ship_type(self, ship_type):
        self.ship_type = ship_type
        print(self.ship_type)

    def set_ship(self, x, y):
        check = self.check_position(x, y)
        print(self.ships)
        print(check)
        if check:
            if self.ships_count[self.ship_type - 1] <= 0:
                return
            self.ships_count[self.ship_type - 1] -= 1
            if self.orientation == 'g':
                for i in range(y, y + self.ship_type):
                    self.ships[x][i] = 1
                    self.ships[x - 1][i] = self.ships[x + 1][i] = 2
                self.ships[x - 1][y - 1] = self.ships[x][y - 1] = self.ships[x + 1][y - 1] = 2
                self.ships[x - 1][y + self.ship_type] = self.ships[x][y + self.ship_type] = self.ships[x + 1][y + self.ship_type] = 2
            if self.orientation == 'v':
                for i in range(x, x + self.ship_type):
                    self.ships[i][y] = 1
                    self.ships[i][y - 1] = self.ships[i][y + 1] = 2
                self.ships[x - 1][y - 1] = self.ships[x - 1][y] = self.ships[x - 1][y + 1] = 2
                self.ships[x + self.ship_type][y - 1] = self.ships[x + self.ship_type][y] = self.ships[x + self.ship_type][y + 1] = 2
        self.draw_ships()

    def go_to_game_page(self):
        if sum(self.ships_count) != 0:
            return
        global game_page

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 8000))
        client.send(pickle.dumps(self.ships))

        game_page = GameWin(self.username, self.ships, client)
        game_page.show()

    def check_position(self, x, y):
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

    def delete_all_ships_from_board(self):
        self.ships = [[0 for _ in range(12)] for _ in range(12)]
        self.user_scene.clear()
        self.draw_grid(self.graphicsView, self.user_scene)
        self.ships_count = [4, 3, 2, 1]


class GameWin(QMainWindow, game.Ui_MainWindow, MainDrawer):
    """Класс, который отвечает за окно игры"""
    def __init__(self, username, ships, client):
        super(GameWin, self).__init__()
        self.setupUi(self)
        self.label.setText('Поиск 2 игрока...')
        self.username = username
        self.ships = ships  # не уверен, мб хранить массивы только на сервере, чтобы не было траблов с изменением
        self.client = client
        self.steps = []  # массив полей, куда пользователь уже бил, их скипаем
        self.status = 0

        self.user_scene = QtWidgets.QGraphicsScene()
        self.enemy_scene = QtWidgets.QGraphicsScene()

        new_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_client.connect(('localhost', 8000))

        self.thread1 = QThread()
        self.battle_manager = BattleManager()
        self.battle_manager.client = new_client
        self.battle_manager.moveToThread(self.thread1)
        self.battle_manager.send_data.connect(self.paint)
        self.thread1.started.connect(self.battle_manager.run)
        self.thread1.start()

        self.draw_grid(self.graphicsView, self.user_scene)
        self.draw_grid(self.graphicsView_2, self.enemy_scene)

        self.draw_ships()

        #  Создать label, чтобы пользователю было видно какой у него статус
        answer = self.client.recv(4096).decode('utf-8')
        print(answer)
        if answer == '1':
            self.thread2 = QThread()
            self.start_manager = StartManager()
            self.start_manager.client = self.client
            self.start_manager.moveToThread(self.thread2)
            self.start_manager.change_starting.connect(self.start_game)
            self.thread2.started.connect(self.start_manager.run)
            self.thread2.start()
        else:
            self.client.recv(4096)
            self.status = 1
            self.label.setText('Игра началась!')

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        if self.status != 0:
            position = a0.pos()
            item_pos = self.graphicsView_2.mapFrom(self, position)
            x, y = item_pos.x()//40+1, item_pos.y()//40+1
            print(y, x)
            if 0 < x < 11 and 0 < y < 11:
                self.battle_step(y, x)

    def battle_step(self, x, y):
        self.client.send(pickle.dumps((x, y)))
        print('sended')
        self.steps.append((x, y))
        res = self.client.recv(4096)
        res = int.from_bytes(res, 'little', signed=False)
        print(res)
        if res == 1:
            print(res)
            self.enemy_scene.addRect((y-1) * 40 + 5, (x-1) * 40 + 5, 30, 30, brush=QColor(255, 0, 0))
        elif res == 0:
            self.enemy_scene.addRect((y-1) * 40 + 5, (x-1) * 40 + 5, 30, 30, brush=QColor(0, 0, 255))
        elif res == 2:
            print('ты лох')

    @pyqtSlot(int, int, bool)
    def paint(self, x, y, flag):
        if flag:
            self.user_scene.addRect((y - 1) * 40 + 10, (x - 1) * 40 + 10, 20, 20, brush=QColor(255, 0, 0))
        else:
            self.user_scene.addRect((y - 1) * 40 + 10, (x - 1) * 40 + 10, 20, 20, brush=QColor(0, 0, 0))

    @pyqtSlot(str)
    def start_game(self, answer):
        self.status = 1
        self.label.setText('Игра началась!')


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
        edit_page = EditWin(username)
        edit_page.show()
        self.close()


class BattleManager(QObject):
    running = False
    send_data = pyqtSignal(int, int, bool)
    client = 0

    def run(self):
        while True:
            x, y, flag = pickle.loads(self.client.recv(4096))
            print('да')
            self.send_data.emit(x, y, flag)


class StartManager(QObject):
    running = False
    change_starting = pyqtSignal(str)
    client = 0

    def run(self):
        ans = self.client.recv(4096).decode('utf-8')
        print(ans)
        self.change_starting.emit('да')


if __name__ == '__main__':
    ships = [[2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 0], [2, 1, 2, 2, 2, 1, 1, 2, 1, 1, 2, 0], [2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2], [2, 1, 2, 2, 2, 1, 1, 2, 1, 1, 1, 2], [2, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0], [2, 1, 1, 1, 2, 0, 0, 0, 0, 0, 0, 0], [2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 1, 2, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0]]

    app = QApplication([])

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 8000))
    client.send(pickle.dumps(ships))

    window = GameWin('fuck', ships, client)
    window.show()
    app.exec()
