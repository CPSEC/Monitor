import socket
import sys
import time
from math import sin
import json

sep = '\x1e'

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('127.0.0.1', 13244)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)

header = ['milliseconds', 'as5048a', 'throttle', 'vm', 'angle', 'bias', 'radius', 'hcsr04', 'vp', 'heading', 'roll',
          'pitch', 'ori_x', 'ori_y', 'ori_z', 'ori_w', 'temp_c', 'mag_x', 'mag_y', 'mag_z', 'gyr_x', 'gyr_y', 'gyr_z',
          'acc_x', 'acc_y', 'acc_z', 'lacc_x', 'lacc_y', 'lacc_z', 'gra_x', 'gra_y', 'gra_z']

d = [0.737365723, 106.7478557, 0.7, 8.167968, -0.5670339, 5.1, 30.5, 123.258422762904, 8.195808, 275.25, -3,
        6.3125, -0.05908203125, -0.01763916, 0.672607422, 0.7374267578125, 23, 24.25, 7.5, -46.75, 0, 0.001111111,
        0.001111111, -0.49, -0.93, 8.46, 0.05, 0.12, -1.26, -0.52, -1.08, 9.73]

for i in range(1000):
    time.sleep(0.01)
    try:
        # prepare data
        d[0] = 0.01 * i
        d[1] = 30 * sin(0.1 * i) + 30
        d_dict = dict(zip(header, d))
        message = (json.dumps(d_dict)+sep).encode()

        # Send data
        print('sending {!r}'.format(message))

        start_time = time.time()
        sock.sendall(message)

        # Look for the response
        amount_received = 0
        amount_expected = len(message)-1

        while amount_received < amount_expected:
            data = sock.recv(1024)
            amount_received += len(data)
            print('received {!r}'.format(data))

        end_time = time.time()
        print("--- %s seconds ---" % (end_time - start_time))

    except Exception as err:
        print('closing socket:', err)
        sock.close()

sock.close()
