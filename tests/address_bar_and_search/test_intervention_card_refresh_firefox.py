import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation

LIGHT_MODE_BEFORE_RBG_VALUE = "rgba(207, 207, 216, 0.33)"
DARK_MODE_BEFORE_RGB_VALUE = "rgba(0, 0, 0, 0.33)"

LIGHT_MODE_AFTER_RGB_VALUE = "color(srgb 0 0 0 / 0.6)"
DARK_MODE_AFTER_RGB_VALUE = "color(srgb 0.984314 0.984314 0.996078 / 0.6)"


# Set search region
@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


def test_intervention_card_refresh(driver: Firefox):
    """
    C1365204.1: regular firefox, check the intervention card
    """
    # instantiate objects and type in search bar
    nav = Navigation(driver).open()
    nav.set_awesome_bar()
    nav.type_in_awesome_bar("refresh firefox")

    # get relevant items
    refresh_text = nav.get_element("fx-refresh-text")
    refresh_button = nav.get_element("fx-refresh-button")
    help_menu_button = nav.get_element("fx-refresh-menu")

    # ensure the text is correct
    assert (
        refresh_text.get_attribute("innerHTML")
        == "Restore default settings and remove old add-ons for optimal performance."
    )

    # ensure the color before hover
    button_background = refresh_button.value_of_css_property("background-color")
    assert (
        button_background == LIGHT_MODE_BEFORE_RBG_VALUE
        or button_background == DARK_MODE_BEFORE_RGB_VALUE
    )
    nav.hover_over_element(refresh_button, chrome=True)

    # ensure there is a hover state
    new_button_background = refresh_button.value_of_css_property("background-color")
    assert (
        new_button_background == LIGHT_MODE_AFTER_RGB_VALUE
        or new_button_background == DARK_MODE_AFTER_RGB_VALUE
    )

    # repeated from before but with the 3 dots menu button
    help_menu_background = help_menu_button.value_of_css_property("background-color")
    assert (
        help_menu_background == LIGHT_MODE_BEFORE_RBG_VALUE
        or help_menu_background == DARK_MODE_BEFORE_RGB_VALUE
    )
    assert help_menu_button.get_attribute("open") is None
    nav.hover_over_element(help_menu_button, chrome=True)

    new_help_menu_background = help_menu_button.value_of_css_property(
        "background-color"
    )
    assert (
        new_help_menu_background == LIGHT_MODE_AFTER_RGB_VALUE
        or new_help_menu_background == DARK_MODE_AFTER_RGB_VALUE
    )

    # ensure the popup appears
    help_menu_button.click()
    assert help_menu_button.get_attribute("open") == "true"
    assert nav.get_element("fx-refresh-menu-get-help-item-get-help") is not None

    # get the number of options (search results)
    search_results_container = nav.get_element("search-results-container")
    search_results = nav.get_all_children(search_results_container, chrome=True)
    assert len(search_results) == 2
