import pytest


@pytest.fixture()
def suite_id():
    return ("various", "Incident Testing for Emergency Releases")


@pytest.fixture()
def set_prefs():
    return [
        ("browser.toolbars.bookmarks.visibility", "always"),
        ("browser.search.region", "US"),
    ]
