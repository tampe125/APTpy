from abstract import AbstractModule


class ShellModule(AbstractModule):
    def _execute(self):
        if not self.cmd:
            return

        print self.cmd
        self.queue_send.put("something something\n")
        self.cmd = ''
