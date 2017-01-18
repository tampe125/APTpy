import threading
from time import sleep
from abc import ABCMeta, abstractmethod


class AbstractChannel(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, client_id, queue_send, queue_recv):
        super(AbstractChannel, self).__init__()
        self.client_id = client_id
        self.connection = None
        self.connect()
        self.queue_send = queue_send
        self.queue_recv = queue_recv
        self.running = True

    def connect(self):
        pass

    def send(self, message):
        pass

    def receive(self):
        pass

    def run(self):
        while self.running:
            sleep(1)

            if not self.queue_send.empty():
                msg = self.queue_send.get()
                self.send(msg)
                self.queue_send.task_done()

            if self.queue_recv.empty():
                msg = self.receive()
                if msg:
                    self.queue_recv.put(msg)
