import logging

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import Navigation
from modules.util import Utilities

ALLOWED_RGB_BEFORE_VALUES_CARD = set(["rgba(0, 0, 0, 0)"])
ALLOWED_RGB_AFTER_VALUES_CARD = set(
    ["color(srgb 0.878824 0.878824 0.885882)", "color(srgb 0.334902 0.331765 0.36)"]
)
ALLOWED_RGB_VALUES_BEFORE_THREE_DOTS = set(
    [
        "color(srgb 0.356863 0.356863 0.4 / 0.07)",
        "color(srgb 0.984314 0.984314 0.996078 / 0.07)",
    ]
)
ALLOWED_RGB_AFTER_VALUES_THREE_DOTS = set(
    [
        "color(srgb 0.356863 0.356863 0.4 / 0.14)",
        "color(srgb 0.984314 0.984314 0.996078 / 0.14)",
    ]
)

REQUIRED_CONTEXT_MENU_ACTIONS_REGULAR_TILE = set(
    ["Pin", "Edit", "Open in a New Window", "Open in a New Private Window", "Dismiss"]
)

REQUIRED_CONTEXT_MENU_ACTIONS_SPONSORED_TILE = set(
    ["Open in a New Window", "Open in a New Private Window", "Dismiss", "Our sponsors &amp; your privacy"]
)

# first value in a tuple is the index of the card, second is the status of sponsorship
card_indices = [(3, False), (0, True)]

@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


def test_default_tile_hover_states(driver: Firefox):
    """
    C1533798.1: Ensure that hover states work correctly
    """
    # instantiate objects
    nav = Navigation(driver).open()
    tabs = TabBar(driver)

    # open a new tab and switch to it
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])
    top_card = nav.get_element("sponsored-site-card")

    # assert the hover state
    assert (
        top_card.value_of_css_property("background-color")
        in ALLOWED_RGB_BEFORE_VALUES_CARD
    )
    tabs.hover_over_element(top_card)
    assert (
        top_card.value_of_css_property("background-color")
        in ALLOWED_RGB_AFTER_VALUES_CARD
    )

    three_dot_menu = nav.get_element("sponsored-site-card-menu-button")

    # assert the hover state again for the three dots
    assert (
        three_dot_menu.value_of_css_property("background-color")
        in ALLOWED_RGB_VALUES_BEFORE_THREE_DOTS
    )
    tabs.hover_over_element(three_dot_menu)
    assert (
        three_dot_menu.value_of_css_property("background-color")
        in ALLOWED_RGB_AFTER_VALUES_THREE_DOTS
    )

@pytest.mark.parametrize("index, sponsored", card_indices)
def test_tile_context_menu_options(driver: Firefox, index: int, sponsored: bool):
    """
    C1533798.2: Ensure that a website has the appropriate context menu actions in the tile.
    """
    # initialize objects
    nav = Navigation(driver).open()
    tabs = TabBar(driver)
    util = Utilities()

    # open a new tab, switch to it and get the sponsored card
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])
    suggested_cards = nav.get_element("sponsored-site-card", multiple=True)

    # pick the fourth card since it is not a sponsored tile
    card = suggested_cards[index]
    nav.hover_over_element(card)

    # press the three dots option
    three_dot_menu = nav.get_element(
        "sponsored-site-card-menu-button", parent_element=card
    )
    three_dot_menu.click()

    # get all of the context menu actions
    context_menu_list = nav.get_element("sponsored-site-context-menu-list")
    child_options = nav.get_all_children(context_menu_list)
    logging.info(f"There are {len(child_options)} context options")

    # match appropriate regex to extract the word of the context menu option
    option_html_logs = [
        option.get_attribute("innerHTML")
        for option in child_options
        if option.get_attribute("innerHTML") != ""
    ]

    matched_regex = util.match_regex(
        r"<button[^>]*><span[^>]*>([^<]*)</span></button>", option_html_logs
    )

    # according to the status of sponsored, look at different context menu actions
    set_in_use = set()
    if sponsored:
        set_in_use = REQUIRED_CONTEXT_MENU_ACTIONS_SPONSORED_TILE
    else:
        set_in_use = REQUIRED_CONTEXT_MENU_ACTIONS_REGULAR_TILE

    # ensure we match each option
    for match in matched_regex:
        if match in set_in_use:
            set_in_use.remove(match)
            logging.info(f"Detected the context item: {match}")

    assert (
        len(set_in_use) == 0
    ), "Did not find all of the required context menu actions."
