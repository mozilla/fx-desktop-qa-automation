from platform import system

import pytest
from selenium.common import TimeoutException
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, PanelUi, TabBar
from modules.browser_object_navigation import Navigation
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "1771617"


MORE_TOOLS_PT = "Mais ferramentas"
DUPLICATE_TAB_PT = "Duplicar aba"
SCREEN_CAP_LABEL_FRONT_PT = "Permitir que"
SCREEN_CAP_LABEL_BACK_PT = "veja sua tela?"


@pytest.fixture()
def test_url(driver):
    return (
        "https://emilghitta.github.io/TestPages/TestCases/ScreenShare/ShareScreen.html"
    )


@pytest.fixture()
def add_to_prefs_list():
    return [("services.sync.prefs.sync-seen.intl.accept_languages", True)]


@pytest.fixture()
def temp_selectors():
    return {
        "start": {
            "selectorData": "start",
            "strategy": "id",
            "groups": ["doNotCache"],
        }
    }


def test_lang_pack_changed_from_about_prefs(
    driver: Firefox,
    nav: Navigation,
    about_prefs: AboutPrefs,
    panel_ui: PanelUi,
    tabs: TabBar,
    test_url: str,
    generic_page: GenericPage,
    temp_selectors,
):
    """
    C1771617 - The language can be changed in about:preferences.
    We choose to set a pref rather than use a non-US local build.
    """
    # Skip Developer Edition since modifying menus, messages, and notifications language is blocked and defaults to
    # English
    try:
        if nav.element_exists("developer-tool-button"):
            pytest.skip(
                "Skipping test: Developer Edition detected dev tools button presence."
            )
    except TimeoutException:
        pass  # If the element doesn't exist run the test

    # Set the alternative language
    about_prefs.open()
    about_prefs.set_alternative_language("pt-BR")

    # Check Panel UI messages
    panel_ui.open_panel_menu()
    panel_ui.expect_element_attribute_contains("more-tools", "label", MORE_TOOLS_PT)
    panel_ui.click_on("panel-ui-button")

    # Check context menu messages (tabs)
    tabs.context_click(tabs.get_tab(1))
    tab_context_menu = ContextMenu(driver)
    tab_context_menu.expect_element_attribute_contains(
        "context-menu-duplicate-tab", "label", DUPLICATE_TAB_PT
    )
    tab_context_menu.hide_popup_by_child_node("context-menu-duplicate-tab")

    # Check prompt messages
    generic_page.elements |= temp_selectors
    generic_page.open()
    generic_page.click_on("start")

    # In automation, Windows is putting the popup behind the browser window.
    # A click in the awesomebar magically makes the popup visible.
    if system() == "Windows":
        nav.click_in_awesome_bar()

    nav.element_visible("popup-notification")
    nav.expect_element_attribute_contains(
        "popup-notification", "label", SCREEN_CAP_LABEL_FRONT_PT
    )
    nav.expect_element_attribute_contains(
        "popup-notification", "endlabel", SCREEN_CAP_LABEL_BACK_PT
    )
