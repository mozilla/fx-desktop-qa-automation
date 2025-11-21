import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation


@pytest.fixture()
def test_case():
    return "3028841"


def test_searchmode_update_on_alias_prefix(driver: Firefox):
    """
    C3028841 - Search mode is updated after typing a keyword/alias at the beginning of a non-empty search string
    """

    # Instantiate objects
    nav = Navigation(driver)
