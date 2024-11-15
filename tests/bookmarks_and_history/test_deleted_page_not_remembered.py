import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, PanelUi


@pytest.fixture()
def test_case():
    return "216273"


@pytest.fixture()
def use_profile():
    return "theme_change"


@pytest.mark.headed
def test_deleted_page_not_remembered(driver: Firefox, sys_platform):
    """
    C216273: Verify that the deleted page from the Hamburger History submenu is not remembered or autofilled in the URL bar
    """
    panel_ui = PanelUi(driver)
    panel_ui.open()
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)

    panel_ui.open_history_menu()
    panel_ui.context_click("bookmark-by-title", labels=["Firefox Privacy Notice"])

    context_menu.click_and_hide_menu("context-menu-delete-page")
    nav.type_in_awesome_bar("Firefox Privacy Notice")

    with driver.context(driver.CONTEXT_CHROME):
        nav.expect(lambda _: len(nav.get_elements("results-dropdown")) == 1)
