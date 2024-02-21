import pytest


@pytest.fixture()
def test_opts():
    return [("browser.toolbars.bookmarks.visibility", "always")]
