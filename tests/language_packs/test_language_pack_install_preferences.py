from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions


def test_language_pack_install_about_preferences(driver: Firefox):
    """
    C1549409: language packs can be installed from about:preferences and firefox is correctly localized
    """
    # instantiate objects
    about_prefs = AboutPrefs(driver, category="general").open()
    ba = BrowserActions(driver)
    alternative_button = about_prefs.get_element("language-set-alternatives-button")
    alternative_button.click()

    # press the alternatives button and find italian
    iframe = about_prefs.get_element("browser-popup")
    ba.switch_to_iframe_context(iframe)
    about_prefs.get_element("language-set-alternatives-popup-select-language").click()
    about_prefs.element_clickable(
        "language-set-alternatives-popup-select-language-search-more"
    )
    more_languages_option = about_prefs.get_element(
        "language-set-alternatives-popup-select-language-search-more"
    )
    about_prefs.double_click(more_languages_option)

    # waiting for the language install to be sucessful
    about_prefs.custom_wait(timeout=20).until(
        lambda _: about_prefs.get_element(
            "language-set-alternatives-popup-select-language"
        ).get_attribute("label")
        == "Select a language to add…"
    )

    # activate the italian language
    dropdown_selection = about_prefs.get_element(
        "language-set-alternatives-popup-select-language"
    )
    dropdown_selection.click()
    about_prefs.get_element(
        "language-set-alternatives-popup-select-language-italian"
    ).click()
    dropdown_selection.click()
    about_prefs.get_element("language-add-button").click()
    about_prefs.get_element("language-list-item").click()
    about_prefs.get_element("language-accept-button").click()

    # final asserts to ensure language is set
    ba.switch_to_content_context()
    assert about_prefs.get_element("html-root").get_attribute("lang") == "it"
    assert alternative_button.get_attribute("label") == "Imposta alternative…"
