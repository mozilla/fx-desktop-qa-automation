import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Preferred language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399148"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("intl.multilingual.enabled", True),
        ("intl.multilingual.downloadEnabled", True),
        ("intl.multilingual.liveReload", True),
    ]


LANGUAGES = ["fr", "de"]


def test_preferred_language_can_be_added(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399148 - Language can be added to the 'Preferred language' dropdown.
    """
    about_prefs.open()
    about_prefs.element_visible("browser-language-heading")

    # Only the shipped locale is downloaded when the pane first opens.
    downloaded = about_prefs.get_installed_browser_languages()
    for language in LANGUAGES:
        assert language not in downloaded, f"{language} was already downloaded."

    # Picking a language that isn't downloaded yet installs its language pack.
    for language in LANGUAGES:
        about_prefs.set_alternative_language(language)
        about_prefs.expect(
            lambda _, lang=language: lang
            in about_prefs.get_installed_browser_languages()
        )

    # Reopening the pane still lists every downloaded language.
    about_prefs.open()
    downloaded = about_prefs.get_installed_browser_languages()
    for language in LANGUAGES:
        assert language in downloaded, f"{language} is missing from the dropdown."
