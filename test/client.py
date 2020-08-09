import os
from socket import*
import sys
import select
from datetime import datetime, timedelta
from math import sin
import json
from opencv import ReadFrames

sep = '\x1e'

HOST = '127.0.0.1'
PORT = 13244
sock = socket(AF_INET, SOCK_STREAM)
sock.connect((HOST, PORT))
sock.setblocking(False)
cur = datetime.now()
nxt = cur + timedelta(microseconds=50)
count = 0

path = os.path.split(os.path.realpath(__file__))[0]
v = ReadFrames(os.path.join(path, 'test.mp4'))

header = ['milliseconds', 'as5048a', 'throttle', 'vm', 'angle', 'bias', 'radius', 'hcsr04', 'vp', 'heading', 'roll',
          'pitch', 'ori_x', 'ori_y', 'ori_z', 'ori_w', 'temp_c', 'mag_x', 'mag_y', 'mag_z', 'gyr_x', 'gyr_y', 'gyr_z',
          'acc_x', 'acc_y', 'acc_z', 'lacc_x', 'lacc_y', 'lacc_z', 'gra_x', 'gra_y', 'gra_z']

d = [0.737365723, 106.7478557, 0.7, 8.167968, -0.5670339, 5.1, 30.5, 123.258422762904, 8.195808, 275.25, -3,
        6.3125, -0.05908203125, -0.01763916, 0.672607422, 0.7374267578125, 23, 24.25, 7.5, -46.75, 0, 0.001111111,
        0.001111111, -0.49, -0.93, 8.46, 0.05, 0.12, -1.26, -0.52, -1.08, 9.73]

while True:

    read_sockets, write_sockets, error_sockets = select.select(
        [sock], [sock], [], 0)

    for s in read_sockets:
        data = s.recv(1024)
        if data:
            print('Receive:', data.decode())

    for s in write_sockets:
        cur = datetime.now()
        if cur >= nxt:
            # data
            d[0] = 0.01 * count
            d[1] = 30 * sin(0.1 * count) + 30
            p_dict = {'rspeed': 40,
                      'mp': 3, 'mi': 4, 'md': 5,
                      'sp': 6, 'si': 7, 'sd': 8}
            img = v.read()
            d_dict = {'sensor': dict(zip(header, d)), 'parameter': p_dict, 'image': img.tolist()}

            message = (json.dumps(d_dict) + sep).encode()
            while message:
                try:
                    sent = sock.send(message)
                except BlockingIOError:
                    pass
                else:
                    message = message[sent:]
            # print('send', d_dict)

            nxt = nxt + timedelta(milliseconds=10)
            count += 1

    if count > 1000:
        break

sock.close()


