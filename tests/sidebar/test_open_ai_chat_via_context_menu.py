import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, TabBar

WEBSITE = "https://en.wikipedia.org/wiki/Firefox"


@pytest.fixture()
def test_case():
    return "3197640"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.chat.enabled", True),
    ]


def test_open_ai_chat_via_context_menu(driver: Firefox):
    """
    C3197640 - Verify that the user can Open the AI chat panel from the Tab context menu.
    """
    # Initialize objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    sidebar = Sidebar(driver)
    nav = Navigation(driver)

    # Open test site
    driver.get(WEBSITE)

    # Enable vertical tabs
    nav.toggle_vertical_tabs()

    # Right-click tab → Choose an AI Chatbot → verify panel opens with provider options
    tabs.context_click(tabs.get_tab(1))
    context_menu.context_click("context-ask-chat")
    context_menu.click_choose_ai_chatbot_from_context_menu()
    sidebar.expect_ai_chat_panel_open()
    sidebar.expect_ai_providers_displayed()

    # Select any AI provider, then close the AI chat panel
    sidebar.select_first_ai_provider()
    sidebar.close_ai_chat_panel()

    # Right-click tab → Open Chatbot → verify AI chat panel opens
    tabs.open_and_switch_to_new_tab()
    tabs.context_click(tabs.get_tab(2))
    context_menu.click_open_chatbot_from_context_menu()
    sidebar.expect_ai_chat_sidebar_open()
