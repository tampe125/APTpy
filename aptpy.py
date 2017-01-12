DEBUG = True


class APTpy:
    def __init__(self):
        pass

    def _checkenv(self):
        pass

    def run(self):
        self._checkenv()

try:
    obj = APTpy()
    obj.run()
except:
    if DEBUG:
        print "[!] Operation aborted"
