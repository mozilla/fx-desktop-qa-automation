import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs

# Without this Nightly has no translation models, so the pickers stay disabled.
REMOTE_SETTINGS_SERVER = "https://firefox.settings.services.mozilla.com/v2"

DOWNLOAD_LANGUAGE = "es"
DOWNLOAD_LANGUAGE_NAME = "Spanish"


@pytest.fixture()
def about_prefs_category():
    # The Translations card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3399171"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("browser.translations.enable", True),
        ("services.settings.server", REMOTE_SETTINGS_SERVER),
    ]


def test_languages_can_be_downloaded(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399171 - Languages can be downloaded in the 'Speed up translation' section.
    """
    # Open the Translations sub-pane and download a language from the dropdown.
    about_prefs.open()
    about_prefs.open_more_translation_settings()
    about_prefs.download_translation_language(DOWNLOAD_LANGUAGE)

    # The language shows up in the list once the download is done.
    about_prefs.wait_for_language_download(DOWNLOAD_LANGUAGE)
    about_prefs.element_visible("download-language-item", labels=[DOWNLOAD_LANGUAGE])
    about_prefs.element_attribute_contains(
        "download-language-item",
        "label",
        DOWNLOAD_LANGUAGE_NAME,
        labels=[DOWNLOAD_LANGUAGE],
    )
