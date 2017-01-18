import logging
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
        logging.getLogger('aptpy').debug("Trying to contact the remote server")

        try:
            response = requests.post('http://localhost:8000/',
                                     json={'task': 'ping', 'client_id': self.client_id},
                                     cookies={'XDEBUG_SESSION': 'PHPSTORM'}
                                     )

            if response.status_code != 200:
                logging.getLogger('aptpy').debug("We can't connect to the remote server")
                raise NotAuthorized()

            logging.getLogger('aptpy').debug("Successfully connected to the remote server")
        except requests.ConnectionError:
            logging.getLogger('aptpy').debug("An error occurred while contacting the remote server")

    def send(self, message):
        pass

    def receive(self, size=4096):
        pass
