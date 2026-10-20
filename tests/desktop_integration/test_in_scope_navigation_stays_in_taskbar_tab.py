import pytest
from selenium.webdriver import Firefox

from auto_fxui.browser_object import Navigation
from auto_fxui.page_object import GenericPage

WIKIPEDIA_URL = "https://www.wikipedia.org/"
IN_SCOPE_URL_PART = "en.wikipedia.org"


@pytest.fixture()
def test_case():
    return "3814263"


def test_in_scope_navigation_stays_in_taskbar_tab(driver: Firefox):
    """
    C3814263 - Verify that in scope and in place navigations remain in the web app window
    """

    # Instantiate objects
    nav = Navigation(driver)
    wikipedia = GenericPage(driver, url=WIKIPEDIA_URL).open()

    # Click the "Add tab to taskbar" button, the tab moves into a Taskbar Tabs window
    nav.click_on("taskbar-tabs-button")
    nav.wait_for_taskbar_tab_window()

    # Click a link on the page, the page loads in the same Taskbar Tabs window
    wikipedia.click_on("wiki-english-link")
    wikipedia.url_contains(IN_SCOPE_URL_PART)
    nav.element_exists("taskbar-tab-window-root")
    nav.wait_for_num_windows(1)
