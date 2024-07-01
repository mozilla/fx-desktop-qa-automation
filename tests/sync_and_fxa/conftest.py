import pytest


@pytest.fixture()
def suite_id():
    return ("S2130", "Sync & Firefox Account")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("identity.fxaccounts.autoconfig.uri", "https://accounts.stage.mozaws.net")]
