import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutAddons, AboutPrefs, GenericPage

LANGUAGE_ADDONS_LINK = "https://addons.mozilla.org/en-US/firefox/language-tools/"
LANGUAGES = [("Italiano", "it", "Imposta alternative…")]


@pytest.mark.parametrize("drop_down_name, shortform, localized_text", LANGUAGES)
def test_language_pack_install_from_addons(
    driver: Firefox, drop_down_name: str, shortform: str, localized_text: str
):
    """
    C1549408: verify that installing a language pack from about:addons will correctly change the locale
    """
    # declaring objects and navigating
    generic_page = GenericPage(driver)
    driver.get(LANGUAGE_ADDONS_LINK)

    # ensuring the page was loaded
    generic_page.custom_wait(timeout=20).until(
        lambda _: generic_page.get_element("language-addons-title") is not None
    )

    # grab the appropriate link and wait until the page is loaded
    language_row = generic_page.get_element("language-addons-row")
    generic_page.get_element(
        "language-addons-row-link", parent_element=language_row
    ).click()
    generic_page.custom_wait(timeout=20).until(
        lambda _: generic_page.get_element("language-addons-subpage-header") is not None
    )

    generic_page.get_element("language-addons-subpage-add-to-firefox").click()

    with driver.context(driver.CONTEXT_CHROME):
        # click one for "Add"
        generic_page.get_element("language-install-popup-add").click()
        # click second time for "Okay", the button is not cached which allows for two different buttons to be different
        generic_page.get_element("language-install-popup-add").click()

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
    dropdown.select_option(drop_down_name, double_click=True)

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
