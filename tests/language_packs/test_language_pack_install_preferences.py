from time import sleep

from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions, Utilities


def test_language_pack_install_about_preferences(driver: Firefox):
    """
    C1549409: language packs can be installed from about:preferences and firefox is correctly localized
    """
    about_prefs = AboutPrefs(driver, category="general").open()
    ba = BrowserActions(driver)
    util = Utilities()
    about_prefs.get_element("language-set-alternatives-button").click()

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
    sleep(10)

    about_prefs.custom_wait(timeout=20).until(
        lambda _: about_prefs.get_element(
            "language-set-alternatives-popup-select-language"
        ).get_attribute("label")
        == "Select a language to add…"
    )

    about_prefs.get_element("language-set-alternatives-popup-select-language").click()

    util.write_html_content("contents", driver, False)
    util.write_html_content("contentschrome", driver, True)
