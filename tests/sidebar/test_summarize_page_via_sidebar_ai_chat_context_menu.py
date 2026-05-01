import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar

WEBSITE = "https://en.wikipedia.org/wiki/Firefox"


@pytest.fixture()
def test_case():
    return "3197642"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.chat.enabled", True),
        ("browser.ml.chat.provider", "https://chatgpt.com"),
    ]


def test_summarize_page_via_sidebar_ai_chat_context_menu(driver: Firefox):
    """
    C3197642 - Verify that the entire page can be summarized using the AI chat context menu from the Sidebar.
    """
    # Instantiate objects
    context_menu = ContextMenu(driver)
    sidebar = Sidebar(driver)
    nav = Navigation(driver)

    # Enable vertical tabs and navigate to a page
    nav.toggle_vertical_tabs()
    driver.get(WEBSITE)

    # Open the AI Chat panel from the sidebar
    sidebar.context_click_ai_chat_button()
    context_menu.click_summarize_page_from_sidebar_ai_chat_button()

    # Verify the AI Chat opens inside the Sidebar with the Summarize page button (chat conversation is not accessible)
    sidebar.expect_ai_chat_sidebar_open()
    sidebar.expect_summarize_button_visible()
