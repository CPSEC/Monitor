# source: https://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size

import socket
import sys
import time

sep = '\x1e'

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('', 13244)
print('starting up on {}port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        length = None  # complete data length
        buffer = ""
        while True:
            data = connection.recv(1024)
            # no data
            if not data:
                break

            print('received {!r}'.format(data))
            buffer += data.decode()

            while True:
                # incomplete data
                if sep not in buffer:
                    break
                # get complete data
                length_str, ignored, buffer = buffer.partition(sep)
                length = len(length_str)
                print('\nlength=', length)

                print('\n\n', length_str)
                connection.sendall(length_str.encode())

    finally:
        # Clean up the connection
        connection.close()

