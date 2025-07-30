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


TEST_URL = "https://www.w3schools.com/html/html5_geolocation.asp"


@pytest.fixture()
def temp_selectors():
    return {
        "accept-choices": {
            "selectorData": "accept-choices",
            "strategy": "id",
            "groups": [],
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


def test_allow_permission_on_geolocation_via_w3c_api(driver: Firefox, temp_selectors):
    """
    C15186 - Verify that geolocation is successfully shared when the user allows permission via the W3C Geolocation API
    """

    # Instantiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors
    tabs = TabBar(driver)

    # Wait for the page to fully load and manually address the cookie banner if appears
    nav.wait_for_page_to_load()
    cookie_element = web_page.get_elements("accept-choices")
    if cookie_element:
        cookie_element[0].click()

    # Click the 'Try It' button and Allow the location sharing
    web_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="primary")

    # Check that the location marker is displayed
    # if map is displayed, style attribute will be available
    web_page.element_visible("location-marker")
    assert web_page.get_element("location-marker").get_attribute("style")

    # Open a new tab, because refresh will keep the allow state of the location for one hour or until the tab is closed
    tabs.open_web_page_in_new_tab(web_page, num_tabs=2)

    # Click the 'Try It' button and Allow the location sharing while choose the option Remember this decision
    web_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="primary", remember_this_decision=True)

    # Check that the location marker is displayed
    # if map is displayed, style attribute will be available
    web_page.element_visible("location-marker")
    assert web_page.get_element("location-marker").get_attribute("style")

    # Assert that the permission icon is displayed in address bar when in a new tab
    tabs.open_web_page_in_new_tab(web_page, num_tabs=3)
    with driver.context(driver.CONTEXT_CHROME):
        permission_icon = nav.get_element("permissions-location-icon")
        assert permission_icon.is_displayed()


def test_block_permission_on_geolocation_via_w3c_api(driver: Firefox, temp_selectors):
    """
    C15186 - Verify that geolocation is not shared when the user blocks permission via the W3C Geolocation API
    """

    # Instantiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors
    tabs = TabBar(driver)

    # Wait for the page to fully load and manually address the cookie banner if appears
    nav.wait_for_page_to_load()
    cookie_element = web_page.get_elements("accept-choices")
    if cookie_element:
        cookie_element[0].click()

    # Click the 'Try It' button and Block the location sharing
    web_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="secondary")

    # Check that the location marker is displayed
    # if map is not displayed, style attribute will not be available
    assert not web_page.get_element("location-marker").get_attribute("style")

    # Click the 'Try It' button and Block the location sharing while choose the option Remember this decision
    tabs.open_web_page_in_new_tab(web_page, num_tabs=2)
    web_page.click_on("geolocation-button-selector")
    nav.handle_geolocation_prompt(button_type="secondary", remember_this_decision=True)

    # Check that the location marker is displayed
    # if map is not displayed, style attribute will not be available
    assert not web_page.get_element("location-marker").get_attribute("style")

    # Assert that the permission icon is displayed in address bar when in a new tab
    tabs.open_web_page_in_new_tab(web_page, num_tabs=3)
    with driver.context(driver.CONTEXT_CHROME):
        permission_icon = nav.get_element("permissions-location-icon")
        assert permission_icon.is_displayed()
