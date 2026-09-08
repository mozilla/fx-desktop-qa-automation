import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Website language card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399157"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


LANGUAGES = ["fr", "es"]


def test_website_language_can_be_added(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399157 - Languages in the 'Website language' can be added.
    """
    about_prefs.open()
    about_prefs.element_visible("website-language-heading")

    # Pick each language in the Add language dropdown and add it.
    for language in LANGUAGES:
        about_prefs.add_website_language(language)
        about_prefs.element_visible("website-language-item", labels=[language])

    # Both languages stay listed in the Website language section.
    for language in LANGUAGES:
        about_prefs.element_visible("website-language-item", labels=[language])
