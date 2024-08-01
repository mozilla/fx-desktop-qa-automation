import locale
import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import PanelUi, TabBar, TabContextMenu, Toolbar
from modules.page_object import AboutPrefs, GenericPage

MORE_TOOLS_PT = "Mais ferramentas"
DUPLICATE_TAB_PT = "Duplicar aba"
SCREEN_CAP_URL = (
    "https://emilghitta.github.io/TestPages/TestCases/ScreenShare/ShareScreen.html"
)
SCREEN_CAP_LABEL_FRONT_PT = "Permitir que"
SCREEN_CAP_LABEL_BACK_PT = "veja sua tela?"


@pytest.fixture()
def set_prefs():
    return [("services.sync.prefs.sync-seen.intl.accept_languages", True)]


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
    select.click()
    select.click()
    about_prefs.get_element("language-option-by-code", labels=["pt-BR"]).click()
    select.click()
    about_prefs.get_element("language-settings-add-button").click()
    about_prefs.element_attribute_contains(
        "language-added-list", "last-selected", "locale-pt-BR"
    )
    about_prefs.get_element("language-settings-ok").click()
    panel_ui = PanelUi(driver)
    panel_ui.open_panel_menu()
    panel_ui.element_attribute_contains("more-tools", "label", MORE_TOOLS_PT)
    panel_ui.click_on("panel-ui-button")
    tab_bar = TabBar(driver)
    tab_bar.context_click(tab_bar.get_tab(1))
    tab_context_menu = TabContextMenu(driver)
    tab_context_menu.element_attribute_contains(
        "context-menu-duplicate-tab", "label", DUPLICATE_TAB_PT
    )
    logging.info(tab_context_menu.context)
    logging.info(tab_context_menu.context_id)
    tab_context_menu.hide_popup_by_child_node("context-menu-duplicate-tab")
    screen_cap = GenericPage(driver, url=SCREEN_CAP_URL)
    screen_cap.open()
    screen_cap.find_element("id", "start").click()
    toolbar = Toolbar(driver)
    toolbar.element_visible("popup-notification")
    toolbar.element_attribute_contains(
        "popup-notification", "label", SCREEN_CAP_LABEL_FRONT_PT
    )
    toolbar.element_attribute_contains(
        "popup-notification", "endlabel", SCREEN_CAP_LABEL_BACK_PT
    )
