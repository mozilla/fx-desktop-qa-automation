from time import sleep

from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions


def test_language_pack_install_about_preferences(driver: Firefox):
    """
    C1549409: language packs can be installed from about:preferences and firefox is correctly localized
    """
    about_prefs = AboutPrefs(driver, category="general").open()
    ba = BrowserActions(driver)
    about_prefs.get_element("language-set-alternatives-button").click()

    iframe = about_prefs.get_element("browser-popup")
    ba.switch_to_iframe_context(iframe)
    about_prefs.get_element("language-set-alternatives-popup-select-lanuages").click()
    about_prefs.element_clickable(
        "language-set-alternatives-popup-select-lanuages-search-more"
    )

    with driver.context(driver.CONTEXT_CHROME):
        select_more = about_prefs.get_element(
            "language-set-alternatives-popup-select-lanuages-search-more"
        )
        select_more.click()
    sleep(10)
