import pytest
from selenium.webdriver import Firefox

from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutProtections


@pytest.fixture()
def test_case():
    return "448321"


def test_protection_level_redirect_about_preferences(driver: Firefox):
    """
    C448321 - Clicking Protections Level redirects to about:preferences#privacy
    """

    # Instantiate objects
    protection = AboutProtections(driver)
    tabs = TabBar(driver)

    # Reach "about:protections"
    protection.open()

    # Click on the Manage your privacy and security settings button
    protection.click_on("manage-privacy-security")
    tabs.switch_to_new_tab()

    # You are redirected to the "about:preferences#privacy" page
    protection.url_contains("about:preferences#privacy")
