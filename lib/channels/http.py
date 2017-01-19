import logging
import requests
from abstract import AbstractChannel


class HttpChannel(AbstractChannel):
    def enabled(self):
        response = requests.get('https://www.google.com')

        return response.status_code == 200

    def connect(self):
        logging.getLogger('aptpy').debug("[HTTP] Trying to contact the remote server")

        try:
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post('http://localhost:8000/',
                                     json={'task': 'ping', 'client_id': self.client_id},
                                     cookies=cookies
                                     )

            if response.status_code != 200:
                logging.getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self.connected = False

            logging.getLogger('aptpy').debug("[HTTP] Successfully connected to the remote server")
            self.connected = True

        except requests.ConnectionError:
            logging.getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self.connected = False

    def _send(self):
        pass

    def receive(self):
        try:
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post('http://localhost:8000/',
                                     json={'task': 'get_job', 'client_id': self.client_id},
                                     cookies=cookies
                                     )

            if response.status_code != 200:
                logging.getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self.connected = False
                return

            return response.json()

        except requests.ConnectionError:
            logging.getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self.connected = False
