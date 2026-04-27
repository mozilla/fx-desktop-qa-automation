import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, TabBar
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "15186"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        (
            "geo.provider.network.url",
            "https://www.googleapis.com/geolocation/v1/geolocate?key"
            "=%GOOGLE_LOCATION_SERVICE_API_KEY%",
        )
    ]


@pytest.fixture()
def test_url():
    return "https://www.w3schools.com/html/html5_geolocation.asp"


@pytest.fixture()
def temp_selectors():
    return {
        "cookie-iframe": {
            "selectorData": "fast-cmp-iframe",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "accept-choices": {
            "selectorData": "button[class='fast-cmp-button-primary']",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "geolocation-button-selector": {
            "selectorData": "button.w3-btn",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "location-marker": {
            "selectorData": "mapholder",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
    }


# Test is unstable on Windows GHA because of permission changes on the CI image
def test_allow_permission_on_geolocation_via_w3c_api(
    driver: Firefox,
    nav: Navigation,
    tabs: TabBar,
    test_url: str,
    generic_page: GenericPage,
    temp_selectors,
):
    """
    C15186 - Verify that geolocation is successfully shared when the user allows permission via the W3C Geolocation API
    """

    # Instantiate Objects
    generic_page.open()
    generic_page.elements |= temp_selectors

    # Wait for the page to fully load and manually address the cookie banner if appears
    nav.wait_for_page_to_load()
    cookie_iframe = generic_page.get_elements("cookie-iframe")
    if cookie_iframe:
        generic_page.switch_to_iframe(1)
        generic_page.click_on("accept-choices")
        generic_page.switch_to_default_frame()

    # Click the 'Try It' button and Allow the location sharing
    generic_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="primary")

    # Check that the location marker is displayed
    # if map is displayed, style attribute will be available
    generic_page.element_has_attribute("location-marker", "style")

    # Open a new tab, because refresh will keep the allow state of the location for one hour or until the tab is closed
    tabs.open_single_page_in_new_tab(generic_page, num_tabs=2)

    # Click the 'Try It' button and Allow the location sharing while choose the option Remember this decision
    generic_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="primary", remember_this_decision=True)

    # Check that the location marker is displayed
    # if map is displayed, style attribute will be available
    generic_page.element_has_attribute("location-marker", "style")

    # Assert that the permission icon is displayed in address bar when in a new tab
    tabs.open_single_page_in_new_tab(generic_page, num_tabs=3)
    nav.expect_in_chrome(
        lambda _: nav.get_element("permissions-location-icon").is_displayed()
    )


# Test is unstable on Windows GHA because of permission changes on the CI image
def test_block_permission_on_geolocation_via_w3c_api(
    driver: Firefox,
    nav: Navigation,
    tabs: TabBar,
    test_url: str,
    generic_page: GenericPage,
    temp_selectors,
):
    """
    C15186 - Verify that geolocation is not shared when the user blocks permission via the W3C Geolocation API
    """

    # Instantiate Objects
    generic_page.open()
    generic_page.elements |= temp_selectors

    # Wait for the page to fully load and manually address the cookie banner if appears
    nav.wait_for_page_to_load()
    cookie_iframe = generic_page.get_elements("cookie-iframe")
    if cookie_iframe:
        generic_page.switch_to_iframe(1)
        generic_page.click_on("accept-choices")
        generic_page.switch_to_default_frame()

    # Click the 'Try It' button and Block the location sharing
    generic_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="secondary")

    # Check that the location marker is displayed
    # if map is not displayed, style attribute will be empty
    generic_page.element_attribute_is("location-marker", "style", "")

    # Click the 'Try It' button and Block the location sharing while choose the option Remember this decision
    tabs.open_single_page_in_new_tab(generic_page, num_tabs=2)
    generic_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="secondary", remember_this_decision=True)

    # Check that the location marker is displayed
    # if map is not displayed, style attribute will empty
    generic_page.element_attribute_is("location-marker", "style", "")

    # Assert that the permission icon is displayed in address bar when in a new tab
    tabs.open_single_page_in_new_tab(generic_page, num_tabs=3)
    nav.expect_in_chrome(
        lambda _: nav.get_element("permissions-location-icon").is_displayed()
    )
