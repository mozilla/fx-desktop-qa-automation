import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

SUPPORT_PAGE_URL_PART = "support.mozilla.org"
SUPPORT_PAGE_ARTICLE_PART = "firefox-options-preferences-and-settings"


@pytest.fixture()
def about_prefs_category():
    # The Firefox support card lives in Settings > About Firefox.
    return "about"


@pytest.fixture()
def test_case():
    return "3374344"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_support_get_help(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3374344 - The "Get help" option in the "Firefox support" card works correctly.
    """
    about_prefs.open()

    # Hovering changes the background color of the link, so compare it before and after.
    default_color = about_prefs.get_element(
        "support-get-help-button"
    ).value_of_css_property("background-color")
    about_prefs.hover("support-get-help")
    hover_color = about_prefs.get_element(
        "support-get-help-button"
    ).value_of_css_property("background-color")
    assert hover_color != default_color, "The Get help option has no hover effect"

    # The link has target="_blank", so the support article opens in a new tab.
    about_prefs.click_on("support-get-help")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(SUPPORT_PAGE_URL_PART)
    # The in-product link redirects to the settings article on SUMO.
    about_prefs.url_contains(SUPPORT_PAGE_ARTICLE_PART)
