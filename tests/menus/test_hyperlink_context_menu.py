import pytest
from selenium.webdriver import Firefox

from modules.browser_object import HyperlinkContextMenu, TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "2637621"


def test_open_link_in_new_window(driver: Firefox):
    """
    C2637621.2: open link in new window
    """
    hyperlink_context = HyperlinkContextMenu(driver)
    tabs = TabBar(driver)
    example = ExamplePage(driver)
    example.open()

    # right click the hyperlink
    example.context_click("more-information")

    # click on the open in new window option
    hyperlink_context.click_and_hide_menu("context-menu-open-in-new-window")

    # verify there are two instances (two windows)
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    example.title_contains(example.MORE_INFO_TITLE)
    example.url_contains(example.MORE_INFO_URL)


"""
C2637621.3: open link in new window (private) already covered
"""
