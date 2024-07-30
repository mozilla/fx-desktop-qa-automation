from selenium.webdriver import Firefox
import pytest
import locale

from modules.page_object import AboutPrefs

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
