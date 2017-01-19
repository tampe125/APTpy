import threading
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
        self.running = True

        # Random time for a connection
        max_interval = 30

        if self.debug:
            max_interval = 1

        self.next_try = (randint(1, max_interval) * 15) + time()

        getLogger('aptpy').debug("[CHANNEL] Next connection attempt will be at %s" %
                                 strftime("%Y-%m-%d %H:%M:%S", localtime(self.next_try)))

        # Change it for every client!
        self.queue_file = 'aptpy.queue'

    @abstractmethod
    def enabled(self):
        """
        Is this method really enabled? (ie we have HTTP connection or we can send emails)
        :return:
        """
        return False

    def halt(self):
        self.running = False

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
        pass

    def run(self):
        while self.running:
            sleep(1)

            if time() >= self.next_try:
                if not self.connected:
                    self.connect()

                # TODO Break if we're not connected

                # First of all let's get some more work
                if self.queue_recv.empty():
                    msg = self.receive()
                    if msg:
                        self.queue_recv.put(msg)

                try:
                    self._send()
                    max_interval = 30
                except:
                    # If anything goes wrong try again in a shorter amount of time
                    max_interval = 15

                if self.debug:
                    max_interval = 1

                self.next_try = (randint(1, max_interval) * 15) + time()

                getLogger('aptpy').debug("[CHANNEL] Next connection attempt will be at %s" %
                                         strftime("%Y-%m-%d %H:%M:%S", localtime(self.next_try)))

            if not self.queue_send.empty():
                msg = self.queue_send.get()
                self.send(msg)
                self.queue_send.task_done()
