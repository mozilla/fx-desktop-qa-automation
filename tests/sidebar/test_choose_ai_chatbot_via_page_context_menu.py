import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar

WEBSITE = "https://en.wikipedia.org/wiki/Firefox"


@pytest.fixture()
def test_case():
    return "3197641"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.chat.enabled", True),
        ("browser.ml.chat.page", True),
        ("browser.ml.chat.provider", ""),
    ]


def test_choose_ai_chatbot_via_page_context_menu(driver: Firefox):
    """
    C3197641 - Verify that the user is redirected to select an AI provider from the Page Context menu.
    """
    # Instantiate objects
    context_menu = ContextMenu(driver)
    sidebar = Sidebar(driver)
    nav = Navigation(driver)

    # Enable vertical tabs and navigate to a page
    nav.toggle_vertical_tabs()
    driver.get(WEBSITE)

    # Right-click the page and select Ask an AI Chatbot > Choose an AI Chatbot
    nav.open_page_context_menu()
    context_menu.click_choose_ai_chatbot_from_context_menu(source="page")

    # Verify the user is redirected to the AI provider selection page in the Sidebar
    sidebar.expect_ai_chat_panel_open()
    sidebar.expect_ai_providers_displayed()
