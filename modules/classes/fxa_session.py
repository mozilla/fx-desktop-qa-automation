import logging

from fxa.core import Client


class FxaSession:
    def __init__(self, url: str, password: str, restmail_session):
        self.client = Client(url)
        self.restmail = restmail_session
        self.password = password
        self.session = None

        logging.info(self.restmail.email)
        logging.info("[password redacted]")

    def create_account(self):
        self.session = self.client.create_account(self.restmail.email, self.password)

    def destroy_account(self):
        self.client.destroy_account(self.restmail.email, self.password)
