import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, TabBar

WEBSITE = "https://en.wikipedia.org/wiki/Firefox"


@pytest.fixture()
def test_case():
    return "3197638"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.chat.enabled", True),
        ("browser.ml.chat.provider", "https://chatgpt.com"),
    ]


def test_summarize_page_via_tab_context_menu(driver: Firefox):
    """
    C3197638 - Verify that an entire page can be summarized using the Tab context menu entry point.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    sidebar = Sidebar(driver)
    nav = Navigation(driver)

    # Enable vertical tabs
    nav.toggle_vertical_tabs()

    # Navigate to a website
    driver.get(WEBSITE)

    # Right-click the tab and select AI Chat
    tabs.context_click(tabs.get_tab(1))
    context_menu.click_context_item("context-ask-chat")

    # In the AI Chat submenu, click "Summarize Page"
    context_menu.click_summarize_page_from_ai_chat()

    # Verify the AI Chat opens inside the Sidebar with the Summarize page button (chat conversation is not accessible)
    sidebar.expect_ai_chat_sidebar_open()
    sidebar.expect_summarize_button_visible()
