import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, PanelUi


@pytest.fixture()
def use_profile():
    return "theme_change"


@pytest.mark.headed
def test_deleted_page_not_remembered(driver: Firefox):
    """
    C216273: Verify that the deleted page from the Hamburger History submenu is not remembered or autofilled in the URL bar
    """
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)

    panel_ui.open_history_menu()
    history_items = panel_ui.get_all_history()

    firefox_privacy_notice = history_items[-1]
    panel_ui.context_click(firefox_privacy_notice)

    context_menu.click_and_hide_menu("context-menu-delete-page")
    nav.type_in_awesome_bar("Firefox Privacy Notice")

    with driver.context(driver.CONTEXT_CHROME):
        all_suggested_results = nav.get_elements("results-dropdown")
        assert len(all_suggested_results) == 1
