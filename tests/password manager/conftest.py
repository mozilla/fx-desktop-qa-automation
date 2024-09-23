import pytest


@pytest.fixture()
def suite_id():
    return ("S43517", "Password manager")


@pytest.fixture()
def set_prefs():
    return []
