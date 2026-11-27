"""
C4438278 - Verify that the user can Undo grouping a tab group
After the assistant groups two tabs, Undo on the result card ungroups them.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, tool_call
from selenium.webdriver import Firefox

PROMPT = "Create a tab group with my lasagna and flights tabs"
PAGES = ["lasagna.html", "cookie_recipe.html", "flights.html"]
GROUPED = ["lasagna.html", "flights.html"]


@pytest.fixture()
def test_case():
    return "4438278"


def test_undo_grouping_tabs(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C4438278 - Verify that the user can Undo grouping a tab group
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "group_tabs",
                "ask_confirmation": False,
                "url_tokens": [SmartWindowChat.url_token(page) for page in GROUPED],
                "label": "Trip planning",
            },
            tool_results=1,
        )
    )

    tabs = TabBar(driver)
    chat = smart_window_chat
    tabs.open_urls_in_tabs(tab_pages(PAGES), open_first_in_current_tab=True)
    SmartBar(driver).open_full_page_chat()

    chat.send(PROMPT)
    chat.confirm_tab_action_if_asked()
    grouped_urls = tab_pages(GROUPED)
    tabs.expect_tabs_grouped(grouped_urls)

    chat.undo_last_action()

    tabs.expect_tabs_ungrouped(grouped_urls)
    assert tabs.get_tab_groups() == []
    tabs.expect_tabs_open(tab_pages(PAGES))
