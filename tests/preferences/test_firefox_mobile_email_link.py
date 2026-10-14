import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

MOBILE_PAGE_URL_PART = "mozilla.org"
MOBILE_PAGE_PATH_PART = "get-app"


@pytest.fixture()
def about_prefs_category():
    # The Firefox for mobile card lives in Settings > More from Mozilla.
    return "moreFromMozilla"


@pytest.fixture()
def test_case():
    return "3375214"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_firefox_mobile_email_link(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3375214 - The Firefox for mobile card "Email the download link to your phone" link works correctly.
    """
    about_prefs.open()

    # The link sits under the QR code and opens the get-app page in a new tab.
    about_prefs.click_on("firefox-mobile-email-link")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(MOBILE_PAGE_URL_PART)
    about_prefs.url_contains(MOBILE_PAGE_PATH_PART)
