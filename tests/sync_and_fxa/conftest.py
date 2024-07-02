import logging
from time import sleep

import pytest
from fxa.core import Client
from fxa.errors import OutOfProtocolError
from fxa.tests.utils import TestEmailAccount


@pytest.fixture()
def suite_id():
    return ("S2130", "Sync & Firefox Account")


@pytest.fixture()
def fxa_url(fxa_env):
    if fxa_env == "stage":
        return "https://accounts.stage.mozaws.net"


@pytest.fixture()
def set_prefs(fxa_url):
    """Set prefs"""
    return [("identity.fxaccounts.autoconfig.uri", fxa_url)]


@pytest.fixture()
def new_fxa_prep(fxa_url: str, acct_password: str) -> dict:
    """Create a PyFxA object and return a dict with artifacts"""
    # Create a testing account using an @restmail.net address.
    acct = TestEmailAccount()
    client = Client(fxa_url)
    yield {
        "client": client,
        "restmail": acct,
        "password": acct_password,
        "otp_code": None,
    }
    acct.clear()
    try:
        client.destroy_account(acct.email, acct_password)
    except OutOfProtocolError as e:
        logging.info(repr(e))


@pytest.fixture()
def get_otp_code(new_fxa_prep):
    """Function factory: wait for the OTP email, then return the OTP code"""

    def _get_otp_code() -> str:
        acct = new_fxa_prep["restmail"]
        logging.info("==========")
        for _ in range(60):
            acct.fetch()
            logging.info("---")
            for m in acct.messages:
                logging.info("Email headers")
                logging.info(m["headers"])
                if "x-verify-short-code" in m["headers"]:
                    return m["headers"]["x-verify-short-code"]
            sleep(0.5)
        assert False, f"No OTP code found in {acct.email}."

    return _get_otp_code
