import sqlite3
import threading
from lib.exceptions import *
from logging import getLogger
from os.path import exists as file_exists
from random import randint
from time import sleep, time, strftime, localtime
from abc import ABCMeta, abstractmethod


class AbstractChannel(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, client_id, queue_send, queue_recv, debug=False):
        super(AbstractChannel, self).__init__()

        self.debug = debug
        self.client_id = client_id
        self._key = None
        self.queue_send = queue_send
        self.queue_recv = queue_recv

        self._running = True
        self._next_try = 0

        self.set_next_time()

        # Change it for every client!
        self.db_file = 'aptpy.queue'

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

    def _create_db(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        cur.execute("CREATE TABLE out(id INTEGER PRIMARY KEY, msg TEXT)")

        conn.commit()
        conn.close()

    @abstractmethod
    def enabled(self):
        """
        Is this method really enabled? (ie we have HTTP connection or we can send emails)
        :return:
        """
        return False

    @abstractmethod
    def connect(self):
        pass

    def send(self, message):
        """
        This will actually enqueue the commands to the local storage; they will be sent when we will get the connection
        :param message:
        :return:
        """
        if not file_exists(self.db_file):
            self._create_db()

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        # Sometimes it fails since the table isn't created yet. Let's try very hard to store it
        try:
            cur.execute("INSERT INTO out (id, msg) VALUES(NULL, ?)", (message, ))
            conn.commit()
        except:
            sleep(2)
            cur.execute("INSERT INTO out (id, msg) VALUES(NULL, ?)", (message,))
            conn.commit()

        conn.close()

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

                    if not self._key:
                        self.connect()

                    # Perform remote actions only if we have a key
                    if self._key:
                        # First of all let's get some more work
                        if self.queue_recv.empty():
                            messages = self.receive()
                            if messages:
                                for msg in messages:
                                    self.queue_recv.put(msg)

                        self._send()
                # If we any of those exceptions was raised stop everything
                except (NotAuthorized, RSAFailedSignature) as fatal_error:
                    raise fatal_error
                except BaseException as e:
                    # If anything goes wrong try again in a shorter amount of time
                    max_interval = 15

                self.set_next_time(max_interval)

            if not self.queue_send.empty():
                msg = self.queue_send.get()
                self.send(msg)
                self.queue_send.task_done()
