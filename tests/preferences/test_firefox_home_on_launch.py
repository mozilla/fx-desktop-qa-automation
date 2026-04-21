import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutNewtab


@pytest.fixture()
def test_case():
    return "143543"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.startup.homepage", "about:home"),
        ("browser.newtabpage.activity-stream.testing.shouldInitializeFeeds", "true"),
        ("browser.startup.page", 1),
    ]


def test_firefox_home_on_launch(
    driver: Firefox,
    about_new_tab: AboutNewtab,
):
    """
    C143543: setting the default new window to be Firefox Home
    """

    # Make sure the Firefox Home page is opened on browser launch
    about_new_tab.element_exists("body-logo")
