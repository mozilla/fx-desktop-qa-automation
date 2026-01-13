import pytest
from selenium.webdriver import Firefox

from modules.components.dropdown import Dropdown
from modules.page_object import AboutAddons, AboutPrefs, AmoLanguages


@pytest.fixture()
def test_case():
    return "1549408"


LANGUAGES = [
    (
        "Italiano",
        "LanguageTools-table-row LanguageTools-lang-it",
        "it",
        "Imposta alternative…",
    )
]


@pytest.mark.parametrize(
    "drop_down_name, language_label, shortform, localized_text", LANGUAGES
)
def test_language_pack_install_from_addons(
    driver: Firefox,
    amo_languages: AmoLanguages,
    about_addons: AboutAddons,
    about_prefs: AboutPrefs,
    drop_down_name: str,
    language_label: str,
    shortform: str,
    localized_text: str,
):
    """
    C1549408: verify that installing a language pack from about:addons will correctly change the locale
    """
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

    # perform language changing and assertions in about_prefs
    about_prefs.open()
    language_dropdown = about_prefs.get_element("language-dropdown")

    dropdown = Dropdown(page=about_prefs, root=language_dropdown)
    dropdown.select_option(drop_down_name, double_click=True, wait_for_selection=False)

    about_prefs.expect_element_attribute_is("prefs-html-root", "lang", shortform)
    about_prefs.expect_element_attribute_is(
        "language-set-alternative-button", "label", localized_text
    )
