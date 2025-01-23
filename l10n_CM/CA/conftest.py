import pytest


@pytest.fixture()
def set_prefs():
    return [("browser.search.region", "CA")]
