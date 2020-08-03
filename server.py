from PyQt5.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
import socket
import select
import sys
import queue


# tutorial : https://pymotw.com/2/select/

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

    def __init__(self, message_queues, port=13244, sep='\x1e'):
        super(Server, self).__init__()
        self.port = port
        self.sep = sep
        self.signals = WorkerSignals()
        self.killed = False
        self.message_queues = message_queues

    @pyqtSlot()
    def run(self):
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(False)

        # Bind the socket to the port
        server_address = ('', self.port)
        # print('starting up on {}port {}'.format(*server_address))
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(5)
        # Sockets from which we expect to read
        inputs = [sock]
        # Sockets to which we expect to write
        outputs = []
        # inputs buffer
        buffer = ""
        #
        noDataCount = {}

        while inputs:
            if self.killed:
                sock.close()
                return

            # Wait for at least one of the sockets to be ready for processing
            readable, writable, exceptional = select.select(inputs, outputs, inputs, 0)

            # Handle inputs
            for s in readable:

                if s is sock:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    connection.setblocking(False)
                    inputs.append(connection)
                    outputs.append(connection)
                    self.signals.connected.emit(str(client_address))

                    # Give the connection a queue for data we want to send
                    self.message_queues[connection] = queue.Queue()
                    noDataCount[connection] = 0
                else:
                    data = s.recv(1024)
                    if data:
                        # A readable client socket has data
                        # print >> sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
                        buffer += data.decode()
                        noDataCount[s] = 0
                        while True:
                            # incomplete data
                            if self.sep not in buffer:
                                break
                            # get complete data
                            length_str, ignored, buffer = buffer.partition(self.sep)
                            self.signals.result.emit(length_str)

                            # message_queues[s].put(data)
                            # if s not in outputs:
                            #     outputs.append(s)

                    else:
                        noDataCount[s] += 1
                        if noDataCount[s] > 10000:
                            self.signals.closed.emit(str(s.getpeername()))
                            if s in outputs:
                                outputs.remove(s)
                            inputs.remove(s)
                            s.close()
                            del self.message_queues[s]
                            del noDataCount[s]

            # Handle outputs
            for s in writable:
                try:
                    next_msg = self.message_queues[s].get_nowait()
                except (queue.Empty, KeyError):
                    pass
                else:
                    s.send(next_msg)

            # Handle "exceptional conditions"
            for s in exceptional:
                # Stop listening for input on the connection
                self.signals.closed.emit(s.getpeername())
                inputs.remove(s)
                if s in outputs:
                    outputs.remove(s)
                    s.close()

                # Remove message queue
                del self.message_queues[s]
                del noDataCount[s]

    def kill(self):
        self.killed = True
