import pickle
import socket
from itertools import cycle

BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 8000))

server.listen(2)

gamers = []

for _ in range(2):
    conn, addr = server.accept()

    print(addr)

    data = conn.recv(BUFFER_SIZE)

    user_ships = pickle.loads(data)
    gamers.append((conn, addr, user_ships))
    if _ == 0:
        conn.send('1'.encode('utf-8'))
    else:
        conn.send('2'.encode('utf-8'))

    print(gamers)

"""Статус ответа будет: 0 промах, 1 попадание"""
for i in cycle([0, 1]):
    current_gamer = gamers[i]
    x, y = pickle.loads(current_gamer[0].recv(BUFFER_SIZE))
    # i - 1
    if gamers[i - 1][2][x][y] == 1:
        gamers[i - 1][2][x][y] = 'X'
        gamers[i][0].send('1'.encode('utf-8'))
        gamers[i - 1][0].send(pickle.dumps((x, y)))
    else:
        gamers[i - 1][2][x][y] = '.'
        current_gamer[0].send('0'.encode('utf-8'))
        gamers[i - 1][0].send(pickle.dumps((x, y)))
