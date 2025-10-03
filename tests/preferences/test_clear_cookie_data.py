import sys
from os import environ

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.page_object import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "143627"


WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


def open_clear_cookies_data_dialog(about_prefs: AboutPrefs, ba: BrowserActions):
    """
    Open about:preferences#privacy, show 'Clear Data' dialog, switch into its iframe,
    read 'Cookies and site data' value, then switch back to content context.
    """
    about_prefs.open()
    iframe = about_prefs.press_button_get_popup_dialog_iframe("Clear Data")
    ba.switch_to_iframe_context(iframe)
    value = about_prefs.get_clear_cookie_data_value()
    ba.switch_to_content_context()
    return value

#@pytest.mark.skipif(WIN_GHA, reason="Test unstable in Windows GA, tracked in 1990570")
def test_clear_cookie_data(driver: Firefox):
    """
    C143627: Cookies and site data can be cleared via the 'Clear Data' panel
    """
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    wait = WebDriverWait(driver, 20)

    # 1) Visit a site so Firefox stores site data/cookies
    driver.get("https://www.wikipedia.com")

    # 2) There should be something to clear (> 0)
    initial = open_clear_cookies_data_dialog(about_prefs, ba)
    assert initial > 0, f"Expected cookie/site data > 0 before clearing, got {initial}"

    # 3) Clear the data: open dialog, click 'Clear', then switch back to content
    about_prefs.open()
    iframe = about_prefs.press_button_get_popup_dialog_iframe("Clear Data")
    ba.switch_to_iframe_context(iframe)
    about_prefs.get_element("clear-data-accept-button").click()
    ba.switch_to_content_context()

    # 4) Re-open the dialog and wait until value becomes 0
    def cleared(_):
        return open_clear_cookies_data_dialog(about_prefs, ba) == 0

    wait.until(cleared)

    # 5) Final explicit check
    final = open_clear_cookies_data_dialog(about_prefs, ba)
    assert final == 0, f"Expected 0 after clearing, got {final}"
