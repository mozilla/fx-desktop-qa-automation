from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation, TabBar
from modules.browser_object_hyperlink_context_menu import HyperlinkContextMenu


def test_open_link_in_new_window(driver: Firefox):
    """
    C2637621.2: open link in new window
    """
    nav = Navigation(driver).open()
    hyperlink_context = HyperlinkContextMenu(driver)
    tabs = TabBar(driver)

    # right click the hyperlink
    nav.open()
    driver.get("https://example.com")
    hyperlink = driver.find_element(By.LINK_TEXT, "More information...")
    hyperlink_context.context_click_element(hyperlink)

    # click on the open in new window option

    open_in_new_window = hyperlink_context.get_context_item(
        "context-menu-open-in-new-window"
    )
    hyperlink_context.click_context_item(open_in_new_window)
    hyperlink_context.hide_popup("contentAreaContextMenu", chrome=True)

    # verify there are two instances (two windows)
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    with driver.context(driver.CONTEXT_CONTENT):
        nav.expect(EC.title_contains("Example Domains"))
        assert driver.current_url == "https://www.iana.org/help/example-domains"


def test_open_link_in_private_window(driver: Firefox):
    """
    C2637621.3: open link in new window (private)
    """
    nav = Navigation(driver).open()
    hyperlink_context = HyperlinkContextMenu(driver)
    tabs = TabBar(driver)

    # right click the hyperlink
    nav.open()
    driver.get("https://example.com")
    hyperlink = driver.find_element(By.LINK_TEXT, "More information...")
    hyperlink_context.context_click_element(hyperlink)

    # click on the open in new window option
    open_in_new_window = hyperlink_context.get_context_item(
        "context-menu-open-in-private-window"
    )
    hyperlink_context.click_context_item(open_in_new_window)
    hyperlink_context.hide_popup("contentAreaContextMenu", chrome=True)

    # verify there are two instances (two windows)
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    with driver.context(driver.CONTEXT_CONTENT):
        nav.expect(EC.title_contains("Example Domains"))
        assert driver.current_url == "https://www.iana.org/help/example-domains"

    # verify its in private mode
    with driver.context(driver.CONTEXT_CHROME):
        nav.element_exists("private-browsing-icon")


def test_copy_link(driver: Firefox):
    """
    C2264627.4: Copy the link and verify it was copied
    """
    nav = Navigation(driver).open()
    hyperlink_context = HyperlinkContextMenu(driver)
    tabs = TabBar(driver)

    # right click the hyperlink
    nav.open()
    driver.get("https://example.com")
    hyperlink = driver.find_element(By.LINK_TEXT, "More information...")
    hyperlink_context.context_click_element(hyperlink)

    # click on the open in new window option
    open_in_new_window = hyperlink_context.get_context_item("context-menu-copy-link")
    hyperlink_context.click_context_item(open_in_new_window)
    hyperlink_context.hide_popup("contentAreaContextMenu", chrome=True)

    # open a new tab
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    # # context click and paste
    search_bar = nav.get_awesome_bar()
    nav.context_click_element(search_bar)

    # paste and go
    with driver.context(driver.CONTEXT_CHROME):
        paste_and_go = nav.get_element("context-menu-paste-and-go")
        paste_and_go.click()
        nav.hide_popup_by_child_node(paste_and_go)

    with driver.context(driver.CONTEXT_CONTENT):
        nav.expect(EC.title_contains("Example Domains"))
        assert driver.current_url == "https://www.iana.org/help/example-domains"
