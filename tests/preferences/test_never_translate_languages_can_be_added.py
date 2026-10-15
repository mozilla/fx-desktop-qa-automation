from pathlib import Path
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TranslationsPanel
from modules.page_object import AboutPrefs

# Without this Nightly has no translation models, so the pickers stay disabled.
REMOTE_SETTINGS_SERVER = "https://firefox.settings.services.mozilla.com/v2"

DROPDOWN_LANGUAGE = "es"
PAGE_LANGUAGE = "de"
LOCAL_HTML = "german_article.html"


@pytest.fixture()
def about_prefs_category():
    # The Translations card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399166"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("browser.translations.enable", True),
        ("services.settings.server", REMOTE_SETTINGS_SERVER),
        # Keep the panel from opening on its own so the test drives it.
        ("browser.translations.automaticallyPopup", False),
    ]


@pytest.fixture()
def german_page(tmp_path: Path) -> str:
    """A page in a language other than the browser's."""
    source = Path("data/pages") / LOCAL_HTML
    destination = tmp_path / LOCAL_HTML
    copyfile(source, destination)
    return destination.as_uri()


def test_never_translate_languages_can_be_added(
    driver: Firefox, about_prefs: AboutPrefs, german_page: str
):
    """
    C3399166 - Languages can be added to the 'Never translate these languages' section.
    """
    nav = Navigation(driver)
    translations_panel = TranslationsPanel(driver)

    # Open the Translations sub-pane and add a language from the dropdown.
    about_prefs.open()
    about_prefs.open_more_translation_settings()
    about_prefs.add_never_translate_language(DROPDOWN_LANGUAGE)
    about_prefs.element_visible("never-translate-item", labels=[DROPDOWN_LANGUAGE])

    # Add a second language from a page written in it, via the panel gear menu.
    nav.search(german_page)
    translations_panel.open_panel()
    translations_panel.check_never_translate_language()

    # Nothing requested a translation, so the locale badge should stay absent.
    translations_panel.element_not_visible("translations-urlbar-button-locale")

    # Both languages are listed back on the Translations sub-pane.
    about_prefs.open()
    about_prefs.open_more_translation_settings()
    for language in (DROPDOWN_LANGUAGE, PAGE_LANGUAGE):
        about_prefs.element_visible("never-translate-item", labels=[language])
