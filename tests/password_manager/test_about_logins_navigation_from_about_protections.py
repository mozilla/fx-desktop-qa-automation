import pytest
from selenium.webdriver import Firefox

from auto_fxui.browser_object import TabBar
from auto_fxui.page_object import AboutProtections

ABOUT_LOGINS_PAGE_TITLE = "Passwords"


@pytest.fixture()
def test_case():
    return "2241084"


def test_about_logins_navigation_from_about_protections(
    driver: Firefox, about_protections: AboutProtections
):
    """
    C2241084: Verify the navigation to about:logins from about:protections
    """

    tabs = TabBar(driver)

    about_protections.open()

    # Click on the Save Passwords button in about:protections page
    about_protections.click_on("about-protections-save-passwords-button")

    # Verify that the about:logins page is opened in a new tab
    driver.switch_to.window(driver.window_handles[-1])
    tabs.title_contains(ABOUT_LOGINS_PAGE_TITLE)
