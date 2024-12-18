import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "1365204"


ALLOWED_RGB_BEFORE_VALUES = set(
    ["rgba(207, 207, 216, 0.33)", "color(srgb 0 0 0 / 0.13)", "rgba(0, 0, 0, 0.33)"]
)
ALLOWED_RGB_AFTER_VALUES = set(
    ["color(srgb 0 0 0 / 0.6)", "color(srgb 0.984314 0.984314 0.996078 / 0.6)"]
)


def test_intervention_card_refresh(driver: Firefox):
    """
    C1365204.1: regular firefox, check the intervention card
    """
    # instantiate objects and type in search bar
    nav = Navigation(driver)
    nav.set_awesome_bar()
    nav.type_in_awesome_bar("refresh firefox")

    # ensure the text is correct
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-text").get_attribute("innerHTML")
        == "Restore default settings and remove old add-ons for optimal performance."
    )
    # ensure the color before hover
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-button").value_of_css_property(
            "background-color"
        )
        in ALLOWED_RGB_BEFORE_VALUES
    )
    nav.hover(nav.get_element("fx-refresh-button"))
    # ensure there is a hover state
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-button").value_of_css_property(
            "background-color"
        )
        in ALLOWED_RGB_AFTER_VALUES
    )

    # repeated from before but with the 3 dots menu button
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-menu").value_of_css_property(
            "background-color"
        )
        in ALLOWED_RGB_BEFORE_VALUES
    )
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-menu").get_attribute("open") is None
    )
    nav.hover(nav.get_element("fx-refresh-menu"))
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-menu").value_of_css_property(
            "background-color"
        )
        in ALLOWED_RGB_AFTER_VALUES
    )

    # ensure the popup appears
    nav.click_on("fx-refresh-menu")
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-menu").get_attribute("open") == "true"
    )
    nav.wait.until(
        lambda _: nav.get_element("fx-refresh-menu-get-help-item-get-help") is not None
    )

    # get the number of options (search results)
    search_results_container = nav.get_element("search-results-container")
    nav.wait.until(lambda _: len(nav.get_all_children(search_results_container)) == 2)
