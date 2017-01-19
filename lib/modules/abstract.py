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
        self.running = True

    def halt(self):
        self.running = False

    def run(self):
        while self.running:
            self.event.wait()

            # When I stop the execution, I'll have to raise the event flag for all modules,
            # otherwise they will be stuck on the wait() method forever
            if not self.running:
                break

            # Add some sleep so the clear flag can propagate
            sleep(0.2)

            self._execute()

    @abstractmethod
    def _execute(self):
        pass

    def its_for_me(self, cmd):
        if cmd.get('module') == self.__class__.__name__:
            self.cmd = cmd
            return True

        return False
