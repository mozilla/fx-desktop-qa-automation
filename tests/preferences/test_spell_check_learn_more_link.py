import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

SUPPORT_PAGE_URL_PART = "support.mozilla.org"
SUPPORT_PAGE_ARTICLE_PART = "how-do-i-use-firefox-spell-checker"


@pytest.fixture()
def about_prefs_category():
    # The Spell check card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399180"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_spell_check_learn_more_link(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399180 - Spell check 'Learn more' link opens the correct link.
    """
    about_prefs.open()

    # The link opens the SUMO article in a new tab.
    about_prefs.click_on("spell-check-learn-more")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(SUPPORT_PAGE_URL_PART)
    about_prefs.url_contains(SUPPORT_PAGE_ARTICLE_PART)
