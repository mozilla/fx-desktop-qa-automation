import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AboutPrefs, AmoLanguages

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
    drop_down_name: str,
    language_label: str,
    shortform: str,
    localized_text: str,
):
    """
    C1549408: verify that installing a language pack from about:addons will correctly change the locale
    """
    # instantiate objects
    amo_languages = AmoLanguages(driver).open()

    # ensuring the page was loaded
    amo_languages.wait_for_language_page_to_load()

    # grab the appropriate link and wait until the page is loaded
    amo_languages.find_language_row_and_navigate(language_label)
    amo_languages.get_element("language-addons-subpage-add-to-firefox").click()

    with driver.context(driver.CONTEXT_CHROME):
        # click one for "Add"
        amo_languages.get_element("language-install-popup-add").click()
        # click second time for "Okay", the button is not cached which allows for two different buttons to be different
        amo_languages.get_element("language-install-popup-add").click()

    # ensure that the about:addons has the language listed
    about_addons = AboutAddons(driver).open()
    about_addons.choose_sidebar_option("locale")
    addon_list_parent = about_addons.get_element("languages-addon-list")
    addon_language_cards = about_addons.get_element(
        "languages-addon-list-card", multiple=True, parent_element=addon_list_parent
    )

    # making sure that 1 language was installed
    assert len(addon_language_cards) == 1

    # perform language changing and assertions in about_prefs
    about_prefs = AboutPrefs(driver, category="general").open()
    language_dropdown = about_prefs.get_element("language-dropdown")
    dropdown = about_prefs.Dropdown(page=about_prefs, root=language_dropdown)
    dropdown.select_option(drop_down_name, double_click=True, wait_for_selection=False)

    about_prefs.custom_wait(timeout=15).until(
        lambda _: about_prefs.get_element("html-root").get_attribute("lang")
        == shortform
    )
    assert (
        about_prefs.get_element("language-set-alternatives-button").get_attribute(
            "label"
        )
        == localized_text
    )
