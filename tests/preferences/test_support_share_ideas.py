import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

CONNECT_PAGE_URL_PART = "connect.mozilla.org"


@pytest.fixture()
def about_prefs_category():
    # The Firefox support card lives in Settings > About Firefox.
    return "about"


@pytest.fixture()
def test_case():
    return "3374345"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_support_share_ideas(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3374345 - The "Share ideas and feedback" option in the "Firefox support" card
    works correctly.
    """
    about_prefs.open()

    # Hovering changes the background color of the link, so compare it before and after.
    default_color = about_prefs.get_element(
        "support-share-ideas-button"
    ).value_of_css_property("background-color")
    about_prefs.hover("support-share-ideas")
    hover_color = about_prefs.get_element(
        "support-share-ideas-button"
    ).value_of_css_property("background-color")
    assert hover_color != default_color, (
        "The Share ideas and feedback option has no hover effect"
    )

    # The link has target="_blank", so Mozilla Connect opens in a new tab.
    about_prefs.click_on("support-share-ideas")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(CONNECT_PAGE_URL_PART)
