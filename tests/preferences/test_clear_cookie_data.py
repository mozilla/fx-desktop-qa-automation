import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.page_object import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "143627"


WEBSITE_ADDRESS = "https://www.wikipedia.com"
# WIN_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("win")


def _dialog_options_present(about_prefs: AboutPrefs) -> bool:
    """Return True when the Clear Data dialog options container exists."""
    try:
        about_prefs.get_element("clear-data-dialog-options")
        return True
    except Exception:
        return False


def _open_clear_cookies_data_dialog(
    about_prefs: AboutPrefs, ba: BrowserActions
):
    """
    Open about:preferences#privacy, show the 'Clear Data' dialog, switch into its iframe,
    wait for its option container to be present, read the value, then switch back.
    """
    about_prefs.open()

    # Click the button and grab the dialog iframe element
    dlg_iframe = about_prefs.clear_cookies_and_get_dialog_iframe()

    # Enter dialog iframe
    ba.switch_to_iframe_context(dlg_iframe)

    # Wait for dialog content to be ready (no custom timeout kwarg)
    about_prefs.wait.until(lambda _: _dialog_options_present(about_prefs))

    value = about_prefs.get_clear_cookie_data_value()

    # Always return to the content context
    ba.switch_to_content_context()
    about_prefs.close_dialog_box()
    return value


def test_clear_cookie_data(driver: Firefox):
    """
    C143627: Cookies and site data can be cleared via the "Clear Data" panel
    """
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    wait = WebDriverWait(driver, 20, poll_frequency=0.5)

    # Visit a site to get a cookie added to saved data
    driver.get(WEBSITE_ADDRESS)

    # Open dialog and read current value (must be > 0)
    cookie_value = _open_clear_cookies_data_dialog(about_prefs, ba)
    assert cookie_value > 0, f"Expected cookie/site data > 0, got {cookie_value}"

    # Clear cookies and site data: open the dialog again, wait for iframe, click clear
    about_prefs.open()
    dlg_iframe = about_prefs.clear_cookies_and_get_dialog_iframe()
    wait.until(lambda _: dlg_iframe and dlg_iframe.is_displayed())
    ba.switch_to_iframe_context(dlg_iframe)
    about_prefs.get_element("clear-data-accept-button").click()
    ba.switch_to_content_context()

    # Wait until the dialog reports 0 (reopen/poll via helper)
    wait.until(lambda _: _open_clear_cookies_data_dialog(about_prefs, ba) == 0)

    final_value = _open_clear_cookies_data_dialog(about_prefs, ba)
    assert final_value == 0, f"Expected 0 after clearing, got {final_value}"
