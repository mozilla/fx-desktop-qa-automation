from selenium.webdriver import Firefox

from modules.browser_object import HyperlinkContextMenu, Navigation, TabBar
from modules.page_object import ExamplePage


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


def test_copy_link(driver: Firefox):
    """
    C2264627.4: Copy the link and verify it was copied
    """
    nav = Navigation(driver)
    hyperlink_context = HyperlinkContextMenu(driver)
    tabs = TabBar(driver)
    example = ExamplePage(driver).open()

    # right click the hyperlink
    example.context_click("more-information")

    # click on the open in new window option
    hyperlink_context.click_and_hide_menu("context-menu-copy-link")

    # open a new tab
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    # # context click and paste
    search_bar = nav.get_awesome_bar()
    nav.context_click(search_bar)

    # paste and go
    nav.click_and_hide_menu("context-menu-paste-and-go")

    example.title_contains(example.MORE_INFO_TITLE)
    example.url_contains(example.MORE_INFO_URL)
