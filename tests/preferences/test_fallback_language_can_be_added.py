import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Fallback language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399152"


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


def test_fallback_language_can_be_added(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399152 - Languages can be added to the 'Fallback language' dropdown.
    """
    about_prefs.open()
    about_prefs.element_visible("browser-language-heading")

    # Wait out the async locale list before trusting that a dropdown is absent.
    assert len(about_prefs.get_installed_browser_languages()) == 1, (
        "More than the shipped locale is downloaded."
    )

    # Fallback language needs a second downloaded language, so it is hidden here.
    about_prefs.element_not_visible("browser-language-fallback")

    # Picking a language that isn't downloaded yet, installs its language pack.
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

    # Switching the Preferred language brings up the Fallback language dropdown.
    about_prefs.set_alternative_language(LANGUAGES[0])
    about_prefs.element_visible("browser-language-fallback")

    # Every downloaded language is offered as a fallback, bar the preferred one.
    about_prefs.expect(
        lambda _: LANGUAGES[1] in about_prefs.get_fallback_language_options()
    )
    options = about_prefs.get_fallback_language_options()
    assert LANGUAGES[0] not in options, "The preferred language is offered as fallback."
