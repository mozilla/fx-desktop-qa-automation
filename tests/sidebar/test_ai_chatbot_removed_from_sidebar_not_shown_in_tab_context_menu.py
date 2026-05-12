import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, TabBar

WEBSITE = "https://en.wikipedia.org/wiki/Firefox"


@pytest.fixture()
def test_case():
    return "3197639"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.chat.enabled", True),
        ("browser.ml.chat.page", True),
    ]


def test_ai_chatbot_removed_from_sidebar_not_shown_in_tab_context_menu(driver: Firefox):
    """
    C3197639 - Verify that removing the AI chatbot from the Sidebar settings will not show the option in the Tab Context menu.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    sidebar = Sidebar(driver)
    nav = Navigation(driver)

    # Enable vertical tabs
    nav.toggle_vertical_tabs()

    # Open Customize Sidebar panel and uncheck the AI chatbot tool
    sidebar.click_customize_sidebar()
    sidebar.uncheck_ai_chatbot_in_customize_panel()

    # Open a new tab and navigate to a website
    tabs.open_and_switch_to_new_tab()
    driver.get(WEBSITE)

    # Right-click the new tab and verify the Ask AI chatbot submenu is absent
    tabs.context_click(tabs.get_tab(2))
    context_menu.expect_ask_ai_chat_submenu_absent()
