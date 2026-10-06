from pathlib import Path

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import AboutAddons, AboutPrefs, AmoLanguages


@pytest.fixture()
def about_prefs_category():
    # The Preferred language dropdown lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3987579"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("intl.multilingual.enabled", True),
        ("intl.multilingual.downloadEnabled", True),
        ("intl.multilingual.liveReload", True),
    ]


# Row to install, locale code, and part of its Browser language heading.
INSTALL_ROW = "LanguageTools-table-row LanguageTools-lang-it"
INSTALL_LANGUAGE = "it"
INSTALL_HEADING = "Lingua"

# Row to save as a file, and the name to save it under.
DOWNLOAD_ROW = "LanguageTools-table-row LanguageTools-lang-de"
DOWNLOAD_NAME = "deutsch-language-pack.xpi"
DOWNLOAD_REGEX = r"deutsch-language-pack\.xpi"


@pytest.fixture()
def delete_files_regex_string():
    return DOWNLOAD_REGEX


def test_language_packs_can_be_downloaded_from_about_addons(
    driver: Firefox, about_prefs: AboutPrefs, downloads_folder: str, delete_files
):
    """
    C3987579 - Language packs can be downloaded from about:addons.
    """
    amo_languages = AmoLanguages(driver)
    about_addons = AboutAddons(driver)
    context_menu = ContextMenu(driver)

    # Open the AMO language page.
    amo_languages.open()
    amo_languages.wait_for_language_page_to_load()

    # Install a language pack with Add to Firefox.
    amo_languages.find_language_row_and_navigate(INSTALL_ROW)
    amo_languages.click_on("language-addons-subpage-add-to-firefox")
    amo_languages.confirm_addon_install_popup()

    # The language pack shows up in about:addons.
    about_addons.open()
    about_addons.choose_sidebar_option("locale")
    assert len(about_addons.get_language_addon_list()) == 1

    # Save a different language pack as an xpi file.
    amo_languages.open()
    amo_languages.wait_for_language_page_to_load()
    amo_languages.find_language_row_and_navigate(DOWNLOAD_ROW)
    amo_languages.click_on("language-addons-subpage-version-history")
    # Clicking the link starts an install, so save it with the context menu.
    saved_xpi = Path(downloads_folder) / DOWNLOAD_NAME
    amo_languages.install_mock_file_picker(str(saved_xpi))
    try:
        amo_languages.context_click("language-addons-subpage-download-file")
        context_menu.click_and_hide_menu("context-menu-save-link")
        amo_languages.wait_for_mock_file_picker()
    finally:
        amo_languages.cleanup_mock_file_picker()
    # Firefox makes an empty file first, so wait for it to fill up.
    amo_languages.expect(lambda _: saved_xpi.exists() and saved_xpi.stat().st_size > 0)

    # Switch to the installed language from the Preferred language dropdown.
    about_prefs.open()
    about_prefs.set_alternative_language(INSTALL_LANGUAGE, wait_for_ui=True)
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", INSTALL_HEADING
    )
    about_prefs.element_visible("browser-language-fallback")
