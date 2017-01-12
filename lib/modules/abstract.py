import threading
from time import sleep
from abc import ABCMeta, abstractmethod


class AbstractModule(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, queue_send, event):
        super(AbstractModule, self).__init__()
        self.enabled = False
        self.cmd = None
        self.queue_send = queue_send
        self.event = event

    def run(self):
        while True:
            self.event.wait()

            # Add some sleep so the clear flag can propagate
            sleep(0.2)

            self._execute()

    @abstractmethod
    def _execute(self):
        pass

    def its_for_me(self, cmd):
        if cmd.startswith(self.__class__.__name__):
            self.cmd = cmd
            return True

        return False
