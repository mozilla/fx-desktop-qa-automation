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
        "Lingua",
    )
]


@pytest.mark.parametrize("language_label, shortform, localized_text", LANGUAGES)
def test_language_pack_install_from_addons(
    driver: Firefox,
    language_label: str,
    shortform: str,
    localized_text: str,
):
    """
    C1549408: verify that installing a language pack from about:addons will correctly change the locale
    """
    # Instantiate objects
    amo_languages = AmoLanguages(driver)
    about_addons = AboutAddons(driver)
    about_prefs = AboutPrefs(driver, category="paneLanguages")

    amo_languages.open()

    # Ensuring the page was loaded
    amo_languages.wait_for_language_page_to_load()

    # Grab the appropriate link and wait until the page is loaded
    amo_languages.find_language_row_and_navigate(language_label)
    amo_languages.click_on("language-addons-subpage-add-to-firefox")

    amo_languages.confirm_language_install_popup()

    # Ensure that the about:addons has the language listed
    about_addons.open()
    about_addons.choose_sidebar_option("locale")
    addon_language_cards = about_addons.get_language_addon_list()

    # Making sure that 1 language was installed
    assert len(addon_language_cards) == 1

    # Perform language changing and locale-applied assertion in about_prefs
    about_prefs.open()
    about_prefs.set_alternative_language(shortform)

    about_prefs.open()
    about_prefs.element_attribute_contains(
        "browser-language-heading", "label", localized_text
    )
