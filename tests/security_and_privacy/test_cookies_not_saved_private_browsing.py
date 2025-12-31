import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.browser_object_navigation import Navigation
from modules.page_object import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "101677"


def test_cookies_not_saved_private_browsing(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    nav: Navigation,
    panel_ui: PanelUi,
    ba: BrowserActions,
):
    """
    C101677: ensure that cookies are not saved after using private browsing
    """

    # Open new private window
    panel_ui.open_and_switch_to_new_window("private")

    # Open the Google page and perform a search
    nav.search("hello")

    # Close the page and switch to first tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # Get the cookies
    about_prefs_privacy.open()
    about_prefs_privacy.get_element("cookies-manage-data").click()
    ba.switch_to_iframe_context(about_prefs_privacy.get_iframe())

    # Wait for no children listed in the cookies menu
    about_prefs_privacy.wait_for_no_children("cookies-manage-data-sitelist")
