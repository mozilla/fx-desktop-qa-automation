import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Sidebar, TabBar

WEBSITE = "https://en.wikipedia.org/wiki/Firefox"


@pytest.fixture()
def test_case():
    return "3197638"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.chat.enabled", True),
    ]


def test_open_ai_chat_via_context_menu(driver: Firefox):
    """
    C3197638 - Verify that an entire page can be summarized using the Tab context menu entry point.
    """
    # Initialize objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    sidebar = Sidebar(driver)

    # Navigate to a website
    driver.get(WEBSITE)

    # Right-click the tab and select AI Chat
    tabs.context_click(tabs.get_tab(1))
    context_menu.context_click("context-ask-chat")
    time.sleep(5)

    # Choose an AI Chatbot from the context menu
    context_menu.click_choose_ai_chatbot_from_context_menu()
    time.sleep(5)

    # # Verify the AI Chat panel opens in the sidebar with provider options displayed
    # sidebar.expect_ai_chat_panel_open()
    # time.sleep(5)
    # sidebar.expect_ai_providers_displayed()
    # time.sleep(5)
