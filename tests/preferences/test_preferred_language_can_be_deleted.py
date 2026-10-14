import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Preferred language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399150"


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


def test_preferred_language_can_be_deleted(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399150 - Language can be deleted from the 'Preferred language' dropdown.
    """
    about_addons = AboutAddons(driver)

    about_prefs.open()
    about_prefs.element_visible("browser-language-heading")

    # Picking a language that isn't downloaded yet installs its language pack.
    for language in LANGUAGES:
        about_prefs.set_alternative_language(language)
        about_prefs.expect(
            lambda _, lang=language: (
                lang in about_prefs.get_installed_browser_languages()
            )
        )

    # Reopening the pane still lists every downloaded language.
    about_prefs.open()
    downloaded = about_prefs.get_installed_browser_languages()
    for language in LANGUAGES:
        assert language in downloaded, f"{language} is missing from the dropdown."

    # Each downloaded language has a language pack listed in about:addons.
    about_addons.open()
    about_addons.choose_sidebar_option("locale")
    installed = about_addons.get_language_addon_list()
    assert len(installed) == len(LANGUAGES), (
        f"Expected {len(LANGUAGES)} language packs, found {len(installed)}."
    )

    # Deleting the language packs empties the Languages view.
    for language in LANGUAGES:
        about_addons.remove_language_addon(language)
    about_addons.expect(lambda _: not about_addons.get_language_addon_list())

    # The deleted languages are gone from the dropdown too.
    about_prefs.open()
    downloaded = about_prefs.get_installed_browser_languages()
    for language in LANGUAGES:
        assert language not in downloaded, f"{language} is still in the dropdown."
