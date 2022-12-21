import pickle
import socket
from threading import Thread, Condition
from time import sleep

BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 8000))

server.listen(2)

gamers = []
WHOSE_TURN = 1

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


def drawer(connection, gamer_number, condition, queue, sender_thread):
    while True:
        x, y = pickle.loads(connection.recv(BUFFER_SIZE))
        print(x, y, gamer_number, WHOSE_TURN)
        if gamer_number == WHOSE_TURN:
            with condition:
                print('да')
                if gamers[gamer_number - 2][2][x][y] == 1:
                    flag = True
                    gamers[gamer_number - 2][2][x][y] = 'X'
                    connection.send(int('1').to_bytes(2, 'little', signed=False))
                else:
                    flag = False
                    gamers[gamer_number - 2][2][x][y] = '.'
                    connection.send(int('0').to_bytes(2, 'little', signed=False))
                queue.append((x, y, flag, gamer_number))
                sender_thread.start()
                condition.notify()
                break
        else:
            print('лох')
            connection.send(int('2').to_bytes(2, 'little', signed=False))

    while True:
        print('лох педальный')
        x, y = pickle.loads(connection.recv(BUFFER_SIZE))
        print(x, y, gamer_number, WHOSE_TURN)
        if gamer_number == WHOSE_TURN:
            with condition:
                if gamers[gamer_number - 2][2][x][y] == 1:
                    flag = True
                    gamers[gamer_number - 2][2][x][y] = 'X'
                    connection.send(int('1').to_bytes(2, 'little', signed=False))
                else:
                    flag = False
                    gamers[gamer_number - 2][2][x][y] = '.'
                    connection.send(int('0').to_bytes(2, 'little', signed=False))
                queue.append((x, y, flag, gamer_number))

                condition.notify()
        else:
            print('лох')
            connection.send(int('2').to_bytes(2, 'little', signed=False))


def sender(connection, condition, queue):
    global WHOSE_TURN
    while True:
        with condition:
            x, y, flag, gamer_number = queue.pop()
            connection.send(pickle.dumps((x, y, flag)))
            print(x, y, flag, gamer_number)
            if gamer_number == 1 and not flag:
                print('смена на 2')
                WHOSE_TURN = 2
            elif gamer_number == 2 and not flag:
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

