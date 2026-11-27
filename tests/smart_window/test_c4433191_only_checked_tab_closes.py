"""
C4433191 - Verify that only the selected tab is closed from the Confirmation panel
With three tabs on the confirmation card, unticking two and confirming closes
only the ticked one.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close my flights, lasagna and hotels tabs"
PAGES = ["flights.html", "lasagna.html", "hotels.html", "museums.html"]
CANDIDATES = ["flights.html", "lasagna.html", "hotels.html"]
PINNED = "flights.html"
KEPT_TITLES = [
    "Cheap Flights, Airline Tickets & Airfare Deals",
    "Downtown Hotels Near the Station",
]
CLOSED_TITLE = "The Very Best Lasagna Recipe"


@pytest.fixture()
def test_case():
    return "4433191"


def test_only_checked_tab_closes(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C4433191 - Verify that only the selected tab is closed from the Confirmation panel
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": False,
                "url_tokens": [SmartWindowChat.url_token(page) for page in CANDIDATES],
            },
            tool_results=1,
        )
    )

    tabs = TabBar(driver)
    chat = smart_window_chat
    urls = tab_pages(PAGES)
    tabs.open_urls_in_tabs(urls, open_first_in_current_tab=True)
    tabs.pin_tab(tab_pages([PINNED])[0])
    SmartBar(driver).open_full_page_chat()

    chat.send(PROMPT)

    assert len(chat.get_confirmation_tabs()) == len(CANDIDATES)
    for title in KEPT_TITLES:
        chat.set_confirmation_tab_checked(title, False)
    ticked = [t["label"] for t in chat.get_confirmation_tabs() if t["checked"]]
    assert len(ticked) == 1 and CLOSED_TITLE in ticked[0], ticked

    chat.confirm_action()

    tabs.expect_tabs_closed(tab_pages(["lasagna.html"]))
    tabs.expect_tabs_open(tab_pages(["flights.html", "hotels.html", "museums.html"]))
