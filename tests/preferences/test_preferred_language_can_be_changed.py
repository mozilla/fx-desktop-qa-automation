import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Preferred language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399149"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("intl.multilingual.enabled", True),
        ("intl.multilingual.downloadEnabled", True),
        ("intl.multilingual.liveReload", True),
    ]


# Locale code, and the Browser language heading once that locale is applied.
LANGUAGES = [("fr", "Langue du navigateur"), ("de", "Browser-Sprache")]


def test_preferred_language_can_be_changed(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399149 - Language can be changed from the 'Preferred language' dropdown.
    """
    about_prefs.open()
    about_prefs.element_visible("browser-language-heading")

    # Picking a language that isn't downloaded yet installs its language pack.
    for language, _ in LANGUAGES:
        about_prefs.set_alternative_language(language)
        about_prefs.expect(
            lambda _, lang=language: (
                lang in about_prefs.get_installed_browser_languages()
            )
        )

    # Reopening the pane still lists every downloaded language.
    about_prefs.open()
    downloaded = about_prefs.get_installed_browser_languages()
    for language, _ in LANGUAGES:
        assert language in downloaded, f"{language} is missing from the dropdown."

    # Each switch retranslates the UI and keeps the Fallback language dropdown, non-default only.
    for language, heading in LANGUAGES:
        about_prefs.set_alternative_language(language, wait_for_ui=True)
        about_prefs.element_attribute_contains(
            "browser-language-heading", "label", heading
        )
        about_prefs.element_visible("browser-language-fallback")
