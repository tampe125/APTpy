import requests
from abstract import AbstractChannel
from logging import getLogger


class HttpChannel(AbstractChannel):
    def __init__(self, client_id, queue_send, queue_recv, debug=False):
        super(HttpChannel, self).__init__(client_id, queue_send, queue_recv, debug)

        self._remote_host = 'http://localhost:8000/'

    def enabled(self):
        response = requests.get('https://www.google.com')

        return response.status_code == 200

    def connect(self):
        getLogger('aptpy').debug("[HTTP] Trying to contact the remote server")

        try:
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post(self._remote_host,
                                     json={'task': 'ping', 'client_id': self.client_id},
                                     cookies=cookies
                                     )

            if response.status_code != 200:
                getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self.connected = False

            getLogger('aptpy').debug("[HTTP] Successfully connected to the remote server")
            self.connected = True

        except requests.ConnectionError:
            getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self.connected = False

    def _send(self):
        pass

    def receive(self):
        try:
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post(self._remote_host,
                                     json={'task': 'get_job', 'client_id': self.client_id},
                                     cookies=cookies
                                     )

            if response.status_code != 200:
                getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self.connected = False
                return

            return response.json()

        except requests.ConnectionError:
            getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self.connected = False
