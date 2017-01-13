from subprocess import check_output
from abstract import AbstractModule


class ShellModule(AbstractModule):
    def _execute(self):
        if not self.cmd:
            return

        output = check_output([self.cmd], shell=True).strip()
        self.queue_send.put(output + "\n")
        self.cmd = ''
