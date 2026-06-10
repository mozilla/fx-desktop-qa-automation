import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, Sidebar

WEBSITE = "https://en.wikipedia.org/wiki/Main_Page"

PROVIDERS = [
    "https://chatgpt.com",
    "https://gemini.google.com",
    "https://claude.ai",
    "https://copilot.microsoft.com",
    "https://huggingface.co/chat",
    "https://chat.mistral.ai/chat",
]


@pytest.fixture()
def test_case():
    return "3197643"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.ml.chat.enabled", True),
        ("browser.ml.chat.provider", "https://chatgpt.com"),
    ]


def test_summarize_page_via_ai_chat_panel(driver: Firefox):
    """
    C3197643 - Verify that the entire page can be summarized using the Summarize current page button from each AI chat panel.
    """
    # Instantiate objects
    nav = Navigation(driver)
    sidebar = Sidebar(driver)

    # Enable vertical tabs and navigate to a page
    nav.toggle_vertical_tabs()
    driver.get(WEBSITE)

    # Open the AI Chat panel from the sidebar
    sidebar.open_ai_chat_panel()
    sidebar.expect_ai_chat_sidebar_open()

    # Switch to each available AI engine and verify the Summarize button works for each
    # (chat conversation is not accessible)
    for provider in PROVIDERS:
        sidebar.switch_to_ai_provider(provider)
        sidebar.expect_summarize_button_visible()
        sidebar.click_summarize_button()
