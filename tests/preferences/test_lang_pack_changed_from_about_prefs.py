import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, TabBar, TabContextMenu, Toolbar
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "1771617"


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


def test_lang_pack_changed_from_about_prefs(driver: Firefox):
    """
    C1771617 - The language can be changed in about:preferences.
    We choose to set a pref rather than use a non-US local build.
    """
    about_prefs = AboutPrefs(driver, category="general")
    about_prefs.open()
    about_prefs.set_alternative_language("pt-BR")

    # Check Panel UI messages
    panel_ui = PanelUi(driver)
    panel_ui.open_panel_menu()
    panel_ui.element_attribute_contains("more-tools", "label", MORE_TOOLS_PT)
    panel_ui.click_on("panel-ui-button")

    # Check context menu messages (tabs)
    tab_bar = TabBar(driver)
    tab_bar.context_click(tab_bar.get_tab(1))
    tab_context_menu = TabContextMenu(driver)
    tab_context_menu.element_attribute_contains(
        "context-menu-duplicate-tab", "label", DUPLICATE_TAB_PT
    )
    tab_context_menu.hide_popup_by_child_node("context-menu-duplicate-tab")

    # Check prompt messages
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
