import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation

ALLOWED_RGB_BEFORE_VALUES = set(
    ["rgba(207, 207, 216, 0.33)", "color(srgb 0 0 0 / 0.13)", "rgba(0, 0, 0, 0.33)"]
)
ALLOWED_RGB_AFTER_VALUES = set(
    ["color(srgb 0 0 0 / 0.6)", "color(srgb 0.984314 0.984314 0.996078 / 0.6)"]
)


# Set search region
@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


@pytest.mark.unstable
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
    assert button_background in ALLOWED_RGB_BEFORE_VALUES
    nav.hover_over_element(refresh_button, chrome=True)

    # ensure there is a hover state
    new_button_background = refresh_button.value_of_css_property("background-color")
    assert new_button_background in ALLOWED_RGB_AFTER_VALUES
    # repeated from before but with the 3 dots menu button
    help_menu_background = help_menu_button.value_of_css_property("background-color")
    assert help_menu_background in ALLOWED_RGB_BEFORE_VALUES
    assert help_menu_button.get_attribute("open") is None
    nav.hover_over_element(help_menu_button, chrome=True)

    new_help_menu_background = help_menu_button.value_of_css_property(
        "background-color"
    )
    assert new_help_menu_background in ALLOWED_RGB_AFTER_VALUES

    # ensure the popup appears
    help_menu_button.click()
    assert help_menu_button.get_attribute("open") == "true"
    assert nav.get_element("fx-refresh-menu-get-help-item-get-help") is not None

    # get the number of options (search results)
    search_results_container = nav.get_element("search-results-container")
    search_results = nav.get_all_children(search_results_container, chrome=True)
    assert len(search_results) == 2
