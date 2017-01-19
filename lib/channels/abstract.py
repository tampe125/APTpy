import threading
from lib.exceptions import *
from logging import getLogger
from random import randint
from time import sleep, time, strftime, localtime
from abc import ABCMeta, abstractmethod


class AbstractChannel(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, client_id, queue_send, queue_recv, debug=False):
        super(AbstractChannel, self).__init__()

        self.debug = debug
        self.client_id = client_id
        self.connected = False
        self.queue_send = queue_send
        self.queue_recv = queue_recv

        self._running = True
        self._next_try = 0

        self.set_next_time()

        # Change it for every client!
        self.queue_file = 'aptpy.queue'

    def halt(self):
        self._running = False

    def set_next_time(self, max_interval=30):
        """
        Sets the next execution time randomly
        :param max_interval:
        :return:
        """
        if self.debug:
            max_interval = 1

        self._next_try = (randint(1, max_interval) * 15) + time()

        getLogger('aptpy').debug("[CHANNEL] Next connection attempt will be at %s" %
                                 strftime("%Y-%m-%d %H:%M:%S", localtime(self._next_try)))

    @abstractmethod
    def enabled(self):
        """
        Is this method really enabled? (ie we have HTTP connection or we can send emails)
        :return:
        """
        return False

    def connect(self):
        pass

    def send(self, message):
        """
        This will actually enqueue the commands to the local storage; they will be sent when we will get the connection
        :param message:
        :return:
        """
        with open(self.queue_file, 'ab') as handle:
            handle.write(message)
            handle.write("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    @abstractmethod
    def _send(self):
        """
        Gets the results stored in the local queue and reports them to the remote server
        :return:
        """
        pass

    @abstractmethod
    def receive(self):
        """
        Queries the remote server and fetches the new jobs to do
        :return:
        """
        return []

    def run(self):
        while self._running:
            sleep(1)

            if time() >= self._next_try:
                try:
                    max_interval = 30

                    if not self.connected:
                        self.connect()

                    # First of all let's get some more work
                    if self.queue_recv.empty():
                        messages = self.receive()
                        if messages:
                            for msg in messages:
                                self.queue_recv.put(msg)

                    self._send()
                # If we're not authorized stop everything
                except NotAuthorized as not_auth:
                    raise not_auth
                except:
                    # If anything goes wrong try again in a shorter amount of time
                    max_interval = 15

                self.set_next_time(max_interval)

            if not self.queue_send.empty():
                msg = self.queue_send.get()
                self.send(msg)
                self.queue_send.task_done()
