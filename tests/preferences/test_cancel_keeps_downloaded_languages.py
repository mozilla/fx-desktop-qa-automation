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
    return "3399173"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("browser.translations.enable", True),
        ("services.settings.server", REMOTE_SETTINGS_SERVER),
    ]


def test_cancel_keeps_downloaded_languages(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3399173 - Cancel doesn't remove the language from the 'Speed up translation' section.
    """
    # Open the Translations sub-pane and download a language from the dropdown.
    about_prefs.open()
    about_prefs.open_more_translation_settings()
    about_prefs.download_translation_language(DOWNLOAD_LANGUAGE)

    # The language shows up in the list once the download is done.
    about_prefs.wait_for_language_download(DOWNLOAD_LANGUAGE)
    about_prefs.element_attribute_contains(
        "download-language-item",
        "label",
        DOWNLOAD_LANGUAGE_NAME,
        labels=[DOWNLOAD_LANGUAGE],
    )

    # The delete icon only asks to confirm.
    about_prefs.click_on("download-language-delete-button", labels=[DOWNLOAD_LANGUAGE])
    about_prefs.element_has_text(
        "download-language-delete-confirm-text",
        f"Delete {DOWNLOAD_LANGUAGE_NAME}",
        labels=[DOWNLOAD_LANGUAGE],
    )
    about_prefs.element_attribute_is(
        "download-language-delete-confirm-button",
        "label",
        "Delete",
        labels=[DOWNLOAD_LANGUAGE],
    )
    about_prefs.element_attribute_is(
        "download-language-delete-cancel-button",
        "label",
        "Cancel",
        labels=[DOWNLOAD_LANGUAGE],
    )

    # Cancelling keeps the language, so the row goes back to normal.
    about_prefs.click_on(
        "download-language-delete-cancel-button", labels=[DOWNLOAD_LANGUAGE]
    )
    about_prefs.element_does_not_exist(
        "download-language-delete-confirm-text", labels=[DOWNLOAD_LANGUAGE]
    )
    about_prefs.element_attribute_contains(
        "download-language-item",
        "label",
        DOWNLOAD_LANGUAGE_NAME,
        labels=[DOWNLOAD_LANGUAGE],
    )
