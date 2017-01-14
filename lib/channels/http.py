import requests
from lib.exceptions import *
from abstract import AbstractChannel


class HttpChannel(AbstractChannel):
    def __init__(self, client_id, queue_send, queue_recv):
        # Try to silence insecure platform warnings
        try:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        except ImportError:
            pass

        super(HttpChannel, self).__init__(client_id, queue_send, queue_recv)

    def enabled(self):
        return True

    def connect(self):
        response = requests.post('http://localhost:8000/',
                                 verify=False,
                                 json={'client_id': self.client_id},
                                 cookies={'XDEBUG_SESSION': 'PHPSTORM'}
                                 )

        if response.status_code != 200:
            raise NotAuthorized()

    def send(self, message):
        pass

    def receive(self, size=4096):
        pass
