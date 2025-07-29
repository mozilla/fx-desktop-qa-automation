import logging
from datetime import datetime
from time import sleep

import pytest
from fxa.core import Client
from fxa.errors import OutOfProtocolError
from fxa.tests.utils import TestEmailAccount


class FxaPrep:
    def __init__(self, url: str, password: str):
        self.client = Client(url)
        self.restmail = TestEmailAccount()
        self.password = password
        self.otp_code = None
        logging.info(self.restmail.email)
        logging.info(self.password)

    def create_account(self):
        self.session = self.client.create_account(self.restmail.email, self.password)

    def destroy_account(self):
        self.client.destroy_account(self.restmail.email, self.password)


@pytest.fixture()
def suite_id():
    return ("S2130", "Sync & Firefox Account")


@pytest.fixture()
def fxa_url(fxa_env):
    if fxa_env == "stage":
        return "https://accounts.stage.mozaws.net"
    elif fxa_env == "prod":
        return "https://accounts.firefox.com"


@pytest.fixture()
def start_time():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict, fxa_url):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [("identity.fxaccounts.autoconfig.uri", fxa_url)]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def new_fxa_prep(fxa_url: str, acct_password: str) -> FxaPrep:
    """Create a PyFxA object and return a dict with artifacts"""
    # Create a testing account using an @restmail.net address.
    prep = FxaPrep(fxa_url, acct_password)
    prep.restmail.clear()
    yield prep
    prep.destroy_account()


@pytest.fixture()
def restmail_session(fxa_test_account) -> TestEmailAccount:
    (username, _) = fxa_test_account
    return TestEmailAccount(email=username)


@pytest.fixture()
def create_fxa(new_fxa_prep: FxaPrep, get_otp_code) -> FxaPrep:
    """Create FxA from a PyFxA object"""
    new_fxa_prep.create_account()
    new_fxa_prep.session.verify_email_code(get_otp_code())
    return new_fxa_prep


@pytest.fixture()
def get_otp_code(start_time: str):
    """Function factory: wait for the OTP email, then return the OTP code"""

    def _get_otp_code(restmail: TestEmailAccount) -> str:
        acct = restmail
        code_header_names = ["x-verify-short-code", "x-signin-verify-code"]
        logging.info("==========")
        for _ in range(60):
            acct.fetch()
            logging.info("---")
            for m in acct.messages:
                logging.info("Parsing email message...")
                if m["receivedAt"] < start_time:
                    continue
                for header_name in code_header_names:
                    if header_name in m["headers"]:
                        return m["headers"][header_name]
            sleep(0.5)
        assert False, f"No OTP code found in {acct.email}."

    return _get_otp_code
