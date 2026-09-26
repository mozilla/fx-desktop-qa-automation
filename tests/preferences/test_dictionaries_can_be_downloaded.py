import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AboutPrefs, AmoLanguages

AMO_LANGUAGE_TOOLS_URL = "addons.mozilla.org/en-US/firefox/language-tools"

# Language code on AMO and the dictionary add-on id.
DICTIONARIES = [
    ("ro", "ro-RO@www.archeus.ro"),
    ("it", "it-IT@dictionaries.addons.mozilla.org"),
]


@pytest.fixture()
def about_prefs_category():
    # The Spell check card lives in Settings > Languages.
    return "languages"


@pytest.fixture()
def test_case():
    return "3987577"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_dictionaries_can_be_downloaded(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3987577 - Dictionaries can be downloaded.
    """
    amo_languages = AmoLanguages(driver)
    about_addons = AboutAddons(driver)

    # Download dictionaries opens AMO language tools in a new tab.
    about_prefs.open()
    about_prefs.click_on("download-dictionaries-link")
    about_prefs.wait_for_num_tabs(2)
    about_prefs.switch_to_new_tab()
    about_prefs.url_contains(AMO_LANGUAGE_TOOLS_URL)

    # Install each dictionary from the list.
    for code, _ in DICTIONARIES:
        amo_languages.open()
        amo_languages.wait_for_language_page_to_load()
        amo_languages.click_on("language-addons-dictionary-link", labels=[code])
        amo_languages.element_visible("language-addons-subpage-header")
        amo_languages.click_on("language-addons-subpage-add-to-firefox")
        amo_languages.confirm_addon_install_popup()

    # Every dictionary shows up in about:addons.
    about_addons.open()
    about_addons.choose_sidebar_option("dictionary")
    for _, addon_id in DICTIONARIES:
        about_addons.element_visible("addon-card", labels=[addon_id])
