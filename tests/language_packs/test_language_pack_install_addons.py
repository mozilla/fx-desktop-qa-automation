import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AboutPrefs, AmoLanguages


@pytest.fixture()
def test_case():
    return "1549408"


LANGUAGES = [
    (
        "LanguageTools-table-row LanguageTools-lang-it",
        "it",
    )
]


@pytest.mark.parametrize("language_label, shortform", LANGUAGES)
def test_language_pack_install_from_addons(
    driver: Firefox,
    language_label: str,
    shortform: str,
):
    """
    C1549408: verify that installing a language pack from about:addons will correctly change the locale
    """
    # Instantiate objects
    amo_languages = AmoLanguages(driver)
    about_addons = AboutAddons(driver)
    about_prefs = AboutPrefs(driver, category="paneLanguages")

    amo_languages.open()

    # ensuring the page was loaded
    amo_languages.wait_for_language_page_to_load()

    # grab the appropriate link and wait until the page is loaded
    amo_languages.find_language_row_and_navigate(language_label)
    amo_languages.click_on("language-addons-subpage-add-to-firefox")

    amo_languages.confirm_language_install_popup()

    # ensure that the about:addons has the language listed
    about_addons.open()
    about_addons.choose_sidebar_option("locale")
    addon_language_cards = about_addons.get_language_addon_list()

    # making sure that 1 language was installed
    assert len(addon_language_cards) == 1

    # perform language changing in about_prefs (helper waits for value to propagate)
    about_prefs.open()
    about_prefs.set_alternative_language(shortform)
