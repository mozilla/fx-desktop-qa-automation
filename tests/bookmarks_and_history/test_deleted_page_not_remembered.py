import logging
import platform
from os import environ

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, PanelUi

X_PADDING = 50
if (
    platform.system().lower().startswith("win")
    and environ.get("GITHUB_ACTIONS") == "true"
):
    X_PADDING += 25


@pytest.fixture()
def test_case():
    return "216273"


@pytest.fixture()
def use_profile():
    return "theme_change"


def test_deleted_page_not_remembered(driver: Firefox):
    """
    C216273: Verify that the deleted page from the Hamburger History submenu is not remembered or autofilled in the URL bar
    """
    panel_ui = PanelUi(driver)
    panel_ui.open()
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)

    panel_ui.open_history_menu()
    history_items = panel_ui.get_all_history()

    firefox_privacy_notice = history_items[-1]
    with driver.context(driver.CONTEXT_CHROME):
        x_offset = firefox_privacy_notice.size.get("width") + X_PADDING
        logging.info(x_offset)
        panel_ui.actions.move_to_element_with_offset(
            firefox_privacy_notice, x_offset, 0
        ).click().perform()

    context_menu.click_and_hide_menu("context-menu-delete-page")
    nav.type_in_awesome_bar("Firefox Privacy Notice")

    with driver.context(driver.CONTEXT_CHROME):
        nav.expect(lambda _: len(nav.get_elements("results-dropdown")) == 1)
