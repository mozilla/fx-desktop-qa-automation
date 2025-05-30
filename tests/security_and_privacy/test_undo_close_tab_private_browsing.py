import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "120118"


VISIT_URL = "about:about"


def test_undo_close_tab_private_browsing(driver: Firefox, sys_platform: str):
    """
    C120118: ensure that you can close a tab in private browsing window
    """
    # instantiate objs
    panel_ui = PanelUi(driver)
    panel_ui.open()
    nav = Navigation(driver)
    tabs = TabBar(driver)
    generic_page = GenericPage(driver, url="about:about")

    # open a new private window and open a new tab
    panel_ui.open_and_switch_to_new_window("private")
    panel_ui.open_and_switch_to_new_window("tab")

    # navigate to the URL
    nav.search(VISIT_URL)

    # ensure its loaded
    generic_page.url_contains("about:about")

    # close the most recent window
    cur_tab = tabs.get_tab_by_title("About About")
    tabs.close_tab(cur_tab)

    # ensuring that one of the tabs was closed properly
    tabs.wait_for_num_tabs(2)
    assert len(driver.window_handles) == 2

    # ensure the last tab can be reopened
    with driver.context(driver.CONTEXT_CHROME):
        tabs.reopen_closed_tab_by_keys(sys_platform)
        tabs.wait_for_num_tabs(2)
        tabs.switch_to_new_tab()
        assert nav.is_private()

    logging.info(f"The observed title in the content context is {driver.title}")
    generic_page.url_contains("about:about")
