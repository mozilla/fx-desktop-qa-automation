import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Website language card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399159"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


LANGUAGES = ["fr", "es"]


def test_website_language_can_be_deleted(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399159 - Languages in the 'Website language' section can be deleted.
    """
    about_prefs.open()
    about_prefs.element_visible("website-language-heading")

    for language in LANGUAGES:
        about_prefs.add_website_language(language)
        about_prefs.element_visible("website-language-item", labels=[language])

    # Each Delete button removes only its own row.
    for i, language in enumerate(LANGUAGES):
        about_prefs.remove_website_language(language)
        about_prefs.element_not_visible("website-language-item", labels=[language])
        for remaining in LANGUAGES[i + 1 :]:
            about_prefs.element_visible("website-language-item", labels=[remaining])
