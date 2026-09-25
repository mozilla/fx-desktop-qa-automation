import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

MOBILE_PAGE_URL_PART = "firefox.com"
MOBILE_PAGE_PATH_PART = "/mobile"


@pytest.fixture()
def about_prefs_category():
    # The Firefox for mobile card lives in Settings > More from Mozilla.
    return "moreFromMozilla"


@pytest.fixture()
def test_case():
    return "3375213"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_firefox_mobile_learn_more_link(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3375213 - The Firefox for mobile card "Learn more" link works correctly.
    """
    about_prefs.open()

    # The link redirects to the Firefox mobile page in a new tab.
    about_prefs.click_on("firefox-mobile-learn-more")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(MOBILE_PAGE_URL_PART)
    about_prefs.url_contains(MOBILE_PAGE_PATH_PART)
