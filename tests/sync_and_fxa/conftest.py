import pytest
from fxa.core import Client
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
def new_fxa_prep(fxa_url) -> dict:
    # Create a testing account using an @restmail.net address.
    acct = TestEmailAccount()
    client = Client(fxa_url)
