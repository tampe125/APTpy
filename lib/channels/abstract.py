import threading
from random import randrange
from time import sleep, time
from abc import ABCMeta, abstractmethod


class AbstractChannel(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, client_id, queue_send, queue_recv):
        super(AbstractChannel, self).__init__()
        self.client_id = client_id
        self.connected = False
        self.queue_send = queue_send
        self.queue_recv = queue_recv
        self.running = True

        # Random time for a connection
        self.next_try = randrange(1, 30, 15) + time()

        # Change it for every client!
        self.queue_file = 'aptpy.queue'

    def halt(self):
        self.running = False

    def connect(self):
        pass

    def send(self, message):
        """
            This will actually enqueue the commands to the local storage; they will be sent when we will get the connection
        """
        with open(self.queue_file, 'ab') as handle:
            handle.write(message)
            handle.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    def receive(self):
        pass

    def run(self):
        while self.running:
            sleep(1)

            if time() >= self.next_try:
                if not self.connected:
                    self.connect()
                # TODO Actually try to send the data to the remote server
                self.next_try = randrange(1, 30, 15) + time()

            if not self.queue_send.empty():
                msg = self.queue_send.get()
                self.send(msg)
                self.queue_send.task_done()

            if self.queue_recv.empty():
                msg = self.receive()
                if msg:
                    self.queue_recv.put(msg)
