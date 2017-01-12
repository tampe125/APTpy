import socket
from abstract import AbstractChannel


class HttpChannel(AbstractChannel):
    def enabled(self):
        return True

    def connect(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(('localhost', 10000))
        self.connection.setblocking(0)

    def send(self, message):
        self.connection.sendall(message)

    def receive(self, size=4096):
        try:
            msg = self.connection.recv(size)
        except socket.error:
            msg = ''

        return msg
