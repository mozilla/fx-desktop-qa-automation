import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object_prefs import AboutPrefs

ABOUT_LOGINS_PAGE_TITLE = "Passwords"


@pytest.fixture()
def test_case():
    return "2241081"


def test_about_logins_navigation_from_about_preferences(
    driver: Firefox, about_prefs: AboutPrefs
):
    """
    C2241081 - Verify the navigation to about:logins from about:preferences
    """

    about_prefs.open()

    # Click on Privacy & Security
    about_prefs.click_on("saved-passwords")

    # Verify that the about:logins page is opened
    tabs = TabBar(driver)
    tabs.title_contains(ABOUT_LOGINS_PAGE_TITLE)
