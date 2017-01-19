from json import dumps
from subprocess import check_output, STDOUT
from abstract import AbstractModule


class ShellModule(AbstractModule):
    def _execute(self):
        if not self.cmd:
            return

        try:
            output = check_output([self.cmd], shell=True, stderr=STDOUT).strip()
        except BaseException as e:
            # Do not die if anything wrong appened
            output = "<ERROR> " + str(type(e).__name__) + str(e.message)

        message = {'module': "ShellModule", "cmd": self.cmd, "result": output.decode("utf-8", "ignore")}
        self.queue_send.put(dumps(message, ensure_ascii=False) + "\n")
        self.cmd = ''
