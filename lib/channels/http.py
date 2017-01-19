import logging
import requests
from abstract import AbstractChannel


class HttpChannel(AbstractChannel):
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
                self.connected = False

            logging.getLogger('aptpy').debug("Successfully connected to the remote server")
            self.connected = True

        except requests.ConnectionError:
            logging.getLogger('aptpy').debug("An error occurred while contacting the remote server")
            self.connected = False
