import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Firefox Updates card lives in Settings > About Firefox.
    return "about"


@pytest.fixture()
def test_case():
    return "3374338"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_whats_new_link(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3374338 - The "What's new" link in the Firefox Updates card works correctly.
    """
    about_prefs.open()

    # The link points at the release notes for the build under test.
    release_notes_url = about_prefs.get_element("whats-new-link").get_attribute("href")

    # Hovering changes the link color, so compare it before and after.
    default_color = about_prefs.get_element("whats-new-link").value_of_css_property(
        "color"
    )
    about_prefs.hover("whats-new-link")
    hover_color = about_prefs.get_element("whats-new-link").value_of_css_property(
        "color"
    )
    assert hover_color != default_color, "The What's new link has no hover effect"

    # The link has target="_blank", so the release notes open in a new tab.
    about_prefs.click_on("whats-new-link")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(release_notes_url.split("?")[0])
