import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutNewtab
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
    [
        "Open in a New Window",
        "Open in a New Private Window",
        "Dismiss",
        "Our sponsors &amp; your privacy",
    ]
)

# first value in a tuple is the index of the card, second is the status of sponsorship
card_indices = [(4, False), (0, True)]


def test_default_tile_hover_states(driver: Firefox):
    """
    C1533798.1: Ensure that hover states work correctly
    """
    # instantiate objects
    newtab = AboutNewtab(driver).open()

    top_card = newtab.get_element("sponsored-site-card")

    # assert the hover state
    assert (
        top_card.value_of_css_property("background-color")
        in ALLOWED_RGB_BEFORE_VALUES_CARD
    )

    newtab.hover(top_card)
    top_card = newtab.get_element("sponsored-site-card")
    assert (
        top_card.value_of_css_property("background-color")
        in ALLOWED_RGB_AFTER_VALUES_CARD
    )

    three_dot_menu = newtab.get_element("sponsored-site-card-menu-button")
    # assert the hover state again for the three dots
    assert (
        three_dot_menu.value_of_css_property("background-color")
        in ALLOWED_RGB_VALUES_BEFORE_THREE_DOTS
    )
    newtab.hover(three_dot_menu)
    three_dot_menu = newtab.get_element("sponsored-site-card-menu-button")
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
    newtab = AboutNewtab(driver).open()
    sleep(3)  # allow page to load, waiting for image isn't enough
    util = Utilities()

    suggested_cards = newtab.get_elements("sponsored-site-card")

    # parametrized to pick sponsored and non-sponsored top site cards
    card = suggested_cards[index]
    newtab.hover(card)

    # re-get the elements since they stale on hover
    suggested_cards = newtab.get_elements("sponsored-site-card")
    card = suggested_cards[index]

    # press the three dots option
    three_dot_menu = newtab.get_element(
        "sponsored-site-card-menu-button", parent_element=card
    )
    three_dot_menu.click()

    # get all of the context menu actions
    context_menu_list = newtab.get_element("sponsored-site-context-menu-list")
    child_options = newtab.get_all_children(context_menu_list)
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
