import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

SUPPORT_PAGE_URL_PART = "support.mozilla.org"
SUPPORT_PAGE_ARTICLE_PART = "website-translation"


@pytest.fixture()
def about_prefs_category():
    # The Translations card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399179"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_translations_learn_more_link(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399179 - Translations 'Learn more' link opens the correct link.
    """
    about_prefs.open()

    # The link opens the SUMO article in a new tab.
    about_prefs.click_on("translations-learn-more")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(SUPPORT_PAGE_URL_PART)
    about_prefs.url_contains(SUPPORT_PAGE_ARTICLE_PART)
