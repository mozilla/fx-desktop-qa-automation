from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
import pytest
import locale
from time import sleep

from modules.page_object import AboutPrefs

@pytest.fixture()
def set_prefs():
    return [
        ("services.sync.prefs.sync-seen.intl.accept_languages", True)
    ]

@pytest.fixture()
def change_locale():
    original_locale = locale.getlocale(locale.LC_ALL)
    locale.setlocale(locale.LC_ALL, "en_GB")
    yield True
    if original_locale is None:
        locale.setlocale(locale.LC_ALL, "en_US")
    else:
        locale.setlocale(locale.LC_ALL, original_locale)

def test_lang_pack_changed_from_about_prefs(driver: Firefox, change_locale):
    """C1771617 The language can be changed in about:preferences, locale in non-enUS, Fx in enUS"""
    about_prefs = AboutPrefs(driver, category="general")
    about_prefs.open()
    about_prefs.get_element("language-set-alternative-button").click()
    driver.switch_to.frame(about_prefs.get_iframe())
    select = about_prefs.get_element("language-settings-select")
    select.click()
    search = about_prefs.get_element("language-settings-search")
    search.click()
    about_prefs.driver.execute_script("arguments[0].removeAttribute('open');", select)

    sleep(3)

