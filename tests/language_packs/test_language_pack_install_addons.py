from time import sleep

from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs, AboutAddons, Navigation

def test_language_pack_install_from_addons(driver: Firefox):
    """"
    C1549408: verify that installing a language pack from about:addons will correctly change the locale
    """
    about_prefs = AboutPrefs(driver, category="general")
    about_addons = AboutAddons(driver)
    nav = Navigation(driver).open()

    nav.search("https://addons.mozilla.org/en-US/firefox/language-tools/")
    sleep(10)
