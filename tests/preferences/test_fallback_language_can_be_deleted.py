import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Fallback language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399154"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("intl.multilingual.enabled", True),
        ("intl.multilingual.downloadEnabled", True),
        ("intl.multilingual.liveReload", True),
    ]


PREFERRED = "fr"
FALLBACKS = ["de", "it"]


def test_fallback_language_can_be_deleted(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399154 - Languages from the 'Fallback language' dropdown can be deleted.
    """
    about_addons = AboutAddons(driver)
    languages = [PREFERRED] + FALLBACKS

    about_prefs.open()
    about_prefs.element_visible("browser-language-heading")

    # Picking a language that isn't downloaded yet installs its language pack.
    for language in languages:
        about_prefs.set_alternative_language(language)
        about_prefs.expect(
            lambda _, lang=language: (
                lang in about_prefs.get_installed_browser_languages()
            )
        )

    # Reopening the pane still lists every downloaded language.
    about_prefs.open()
    downloaded = about_prefs.get_installed_browser_languages()
    for language in languages:
        assert language in downloaded, f"{language} is missing from the dropdown."

    # Switching the Preferred language brings up the Fallback language dropdown.
    about_prefs.set_alternative_language(PREFERRED)
    about_prefs.element_visible("browser-language-fallback")

    # Every downloaded language is offered as a fallback, except the preferred one.
    about_prefs.expect(
        lambda _: all(
            lang in about_prefs.get_fallback_language_options() for lang in FALLBACKS
        )
    )

    # Deleting the language packs takes those languages out of about:addons.
    about_addons.open()
    about_addons.choose_sidebar_option("locale")
    for language in FALLBACKS:
        about_addons.remove_language_addon(language)
    about_addons.expect(
        lambda _: (
            len(about_addons.get_language_addon_list())
            == len(languages) - len(FALLBACKS)
        )
    )

    # The deleted languages are gone from the Fallback language dropdown too.
    about_prefs.open()
    about_prefs.element_visible("browser-language-fallback")
    options = about_prefs.get_fallback_language_options()
    for language in FALLBACKS:
        assert language not in options, f"{language} is still offered as a fallback."
