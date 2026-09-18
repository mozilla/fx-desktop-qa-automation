import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Fallback language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399153"


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


def test_fallback_language_can_be_changed(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399153 - The 'Fallback language' can be changed from the dropdown.
    """
    preferred, preferred_heading = LANGUAGES[0]
    fallback = LANGUAGES[1][0]

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

    # Switching the Preferred language retranslates the UI and shows the fallback.
    about_prefs.set_alternative_language(preferred, wait_for_ui=True)
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", preferred_heading
    )
    about_prefs.element_visible("browser-language-fallback")

    # Changing the fallback leaves the browser language on the preferred one.
    about_prefs.set_fallback_language(fallback)
    about_prefs.element_attribute_is("browser-language-preferred", "value", preferred)
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", preferred_heading
    )
