import pickle
import socket
from functools import reduce
from threading import Thread, Condition
from time import sleep

BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 8000))

server.listen(2)

gamers = []
WHOSE_TURN = 1
GAME_END = False

for _ in range(2):
    conn, addr = server.accept()

    data = conn.recv(BUFFER_SIZE)

    user_ships = pickle.loads(data)
    conn1, addr1 = server.accept()
    gamers.append((conn, addr, user_ships, conn1))
    if _ == 0:
        conn.send('1'.encode('utf-8'))
    else:
        conn.send('2'.encode('utf-8'))

sleep(1)

gamers[0][0].send('start'.encode('utf-8'))
gamers[1][0].send('start'.encode('utf-8'))


def check_ships(i, gamer, x, y):
    return (gamer[i - 2][2][x + 1][y] != 1 and gamer[i - 2][2][x - 1][y] != 1 and gamer[i - 2][2][x][y + 1] != 1
            and gamer[i - 2][2][x][y - 1] != 1)


def check_win(i, gamer):
    return reduce(lambda x, y: x + y, [elem.count('X') for elem in gamer[i - 2][2]]) == 20


def user_turn(connection, gamer_number, queue, x, y):
    global GAME_END
    if GAME_END:
        connection.send(int('4').to_bytes(2, 'little', signed=False))
    if gamers[gamer_number - 2][2][x][y] == 1:
        flag = True
        gamers[gamer_number - 2][2][x][y] = 'X'
        win_status = check_win(gamer_number, gamers)
        ch_ship = check_ships(gamer_number, gamers, x, y)
        if win_status:
            GAME_END = True
        if ch_ship:
            connection.send(int('3').to_bytes(2, 'little', signed=False))
        else:
            connection.send(int('1').to_bytes(2, 'little', signed=False))
    else:
        flag = False
        gamers[gamer_number - 2][2][x][y] = '.'
        connection.send(int('0').to_bytes(2, 'little', signed=False))
    queue.append((x, y, flag, gamer_number))


def drawer(connection, gamer_number, condition, queue, sender_thread):
    while True:
        x, y = pickle.loads(connection.recv(BUFFER_SIZE))
        if gamer_number == WHOSE_TURN:
            with condition:
                user_turn(connection, gamer_number, queue, x, y)
                sender_thread.start()
                condition.notify()
                break
        else:
            connection.send(int('2').to_bytes(2, 'little', signed=False))

    while True:
        x, y = pickle.loads(connection.recv(BUFFER_SIZE))
        if gamer_number == WHOSE_TURN:
            with condition:
                user_turn(connection, gamer_number, queue, x, y)
                condition.notify()
        else:
            connection.send(int('2').to_bytes(2, 'little', signed=False))


def sender(connection, condition, queue):
    global WHOSE_TURN
    global GAME_END
    while True:
        with condition:
            x, y, flag, gamer_number = queue.pop()
            connection.send(pickle.dumps((x, y, flag)))
            print(x, y, flag, gamer_number)
            if (gamer_number == 1 and not flag) or GAME_END:
                print('смена на 2')
                WHOSE_TURN = 2
            elif (gamer_number == 2 and not flag) or GAME_END:
                print('смена на 1')
                WHOSE_TURN = 1
            condition.wait()


condition1 = Condition()
condition2 = Condition()

queue1 = []
queue2 = []

gamer_sender_1 = Thread(target=sender, args=(gamers[1][3], condition1, queue1,))
gamer_sender_2 = Thread(target=sender, args=(gamers[0][3], condition2, queue2,))

gamer_drawer_1 = Thread(target=drawer, args=(gamers[0][0], 1, condition1, queue1, gamer_sender_1,))
gamer_drawer_2 = Thread(target=drawer, args=(gamers[1][0], 2, condition2, queue2, gamer_sender_2,))

gamer_drawer_1.start()
gamer_drawer_2.start()

