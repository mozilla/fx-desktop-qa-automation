import pytest


@pytest.fixture()
def set_prefs():
    return [("browser.toolbars.bookmarks.visibility", "always")]
