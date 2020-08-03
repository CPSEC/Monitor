from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
import socket


class WorkerSignals(QObject):
    """
    Signals for Server:
     * connection established
     * connection closed
     * get data from client
    """
    connected = pyqtSignal(str)
    closed = pyqtSignal(str)
    result = pyqtSignal(str)


class Server(QRunnable):
    """
    Server thread
    """

    def __init__(self, port=13244, sep='\x1e'):
        super(Server, self).__init__()
        self.port = port
        self.sep = sep
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ('', self.port)
        # print('starting up on {}port {}'.format(*server_address))
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        while True:
            # Wait for a connection
            print('waiting for a connection')
            connection, client_address = sock.accept()
            try:
                print('connection from', client_address)
                self.signals.connected.emit(str(client_address))

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
                        if self.sep not in buffer:
                            break
                        # get complete data
                        length_str, ignored, buffer = buffer.partition(self.sep)
                        # length = len(length_str)

                        self.signals.result.emit(length_str)
                        print('\n\n', length_str)
                        connection.sendall(length_str.encode())


            finally:
                # Clean up the connection
                connection.close()
                self.signals.closed.emit(str(client_address))
