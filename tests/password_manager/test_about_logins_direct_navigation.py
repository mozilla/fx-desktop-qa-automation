import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object_about_pages import AboutLogins

ABOUT_LOGINS_PAGE_TITLE = "Passwords"


@pytest.fixture()
def test_case():
    return "2241080"


def test_about_logins_direct_navigation(
    driver: Firefox, about_logins: AboutLogins
):
    """
    C2241080 - Verify direct navigation to about:logins
    """

    about_logins.open()

    # Verify that the about:logins page is opened
    tabs = TabBar(driver)
    tabs.title_contains(ABOUT_LOGINS_PAGE_TITLE)
