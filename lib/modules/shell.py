from subprocess import check_output
from abstract import AbstractModule


class ShellModule(AbstractModule):
    def _execute(self):
        if not self.cmd:
            return

        try:
            output = check_output([self.cmd], shell=True).strip()
        except BaseException as e:
            # Do not die if anything wrong appened
            output = "<ERROR> " + str(type(e).__name__) + str(e.message)
        self.queue_send.put(output + "\n")
        self.cmd = ''
