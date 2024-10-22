import time

import pytest
from selenium.common import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, TabBar
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "15186"


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        (
            "geo.provider.network.url",
            "https://www.googleapis.com/geolocation/v1/geolocate?key"
            "=%GOOGLE_LOCATION_SERVICE_API_KEY%",
        )
    ]


TEST_URL = "https://www.w3schools.com/html/html5_geolocation.asp"


def handle_cookie_banner(driver, web_page):
    """
    Address the cookie banner manually if appears, as the cookie banner dismissal preference is not effective in this
    context
    """
    try:
        driver.switch_to.window(driver.window_handles[-1])
        web_page.find_element(By.ID, "accept-choices").click()
    except NoSuchElementException:
        # If the cookie banner is not found, continue with the test
        pass


def handle_geolocation_prompt(nav, button_type="primary"):
    """
    Handles geolocation prompt by clicking either the 'Allow' or 'Block' button based on the button_type provided
    """
    button_selector = f"popup-notification-{button_type}-button"
    nav.element_clickable(button_selector)
    nav.click_on(button_selector)


def click_geolocation_button_trigger(web_page):
    """
    Clicks the 'Try It' button inside the webpage to trigger the geolocation prompt
    """
    geolocation_button_selector = (
        "button.w3-btn.w3-blue.w3-round[onclick='getLocation()']"
    )
    web_page.find_element(By.CSS_SELECTOR, geolocation_button_selector).click()


def is_location_marker_displayed(web_page):
    """
    Checks if the location marker ('You are here!') is displayed on the web page inside the map.
    """
    location_marker = web_page.find_elements(
        By.CSS_SELECTOR, "div[aria-label='You are here!'][role='img']"
    )

    if location_marker:  # Check if the marker exists
        return location_marker[0].is_displayed()
    else:
        return False


def open_web_page_in_new_tab(web_page, driver, tabs, expected_num_tabs):
    """
    Opens a new tab, switches the driver context to the new tab and opens the test webpage
    """
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(expected_num_tabs)
    driver.switch_to.window(driver.window_handles[-1])
    web_page.open()


def test_allow_permission_on_geolocation_via_w3c_api(driver: Firefox):
    """
    C15186 - Verify that geolocation is successfully shared when the user allows permission via the W3C Geolocation API
    """

    # Instantiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    tabs = TabBar(driver)

    # Wait for the page to fully load and manually address the cookie banner if appears
    nav.wait_for_page_to_load()
    handle_cookie_banner(driver, web_page)

    # Click the 'Try It' button and Allow the location sharing
    click_geolocation_button_trigger(web_page)
    handle_geolocation_prompt(nav, button_type="primary")

    # Assert that the location marker is displayed
    assert is_location_marker_displayed(web_page)

    # Open a new tab, because refresh will keep the allow state of the location for one hour or until the tab is closed
    open_web_page_in_new_tab(web_page, driver, tabs, 2)

    # Click the 'Try It' button and Allow the location sharing while choose the option Remember this decision
    click_geolocation_button_trigger(web_page)
    nav.element_clickable("checkbox-remember-this-decision")
    nav.click_on("checkbox-remember-this-decision")
    handle_geolocation_prompt(nav, button_type="primary")

    # Assert that the location marker is displayed again
    assert is_location_marker_displayed(web_page)

    # Assert that the permission icon is displayed in address bar when in a new tab
    open_web_page_in_new_tab(web_page, driver, tabs, 3)
    with driver.context(driver.CONTEXT_CHROME):
        permission_icon = nav.get_element("permissions-location-icon")
        assert permission_icon.is_displayed()


def test_block_permission_on_geolocation_via_w3c_api(driver: Firefox):
    """
    C15186 - Verify that geolocation is not shared when the user blocks permission via the W3C Geolocation API
    """

    # Instantiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    tabs = TabBar(driver)

    # Wait for the page to fully load and manually address the cookie banner if appears
    nav.wait_for_page_to_load()
    handle_cookie_banner(driver, web_page)

    # Click the 'Try It' button and Block the location sharing
    click_geolocation_button_trigger(web_page)
    handle_geolocation_prompt(nav, button_type="secondary")

    # Assert that the location marker is not displayed
    assert not is_location_marker_displayed(web_page)

    # Click the 'Try It' button and Block the location sharing while choose the option Remember this decision
    nav.refresh_page()
    click_geolocation_button_trigger(web_page)
    nav.element_clickable("checkbox-remember-this-decision")
    nav.click_on("checkbox-remember-this-decision")
    handle_geolocation_prompt(nav, button_type="secondary")

    # Assert that the location marker is not displayed
    assert not is_location_marker_displayed(web_page)

    # Assert that the permission icon is displayed in address bar when in a new tab
    open_web_page_in_new_tab(web_page, driver, tabs, 2)
    with driver.context(driver.CONTEXT_CHROME):
        permission_icon = nav.get_element("permissions-location-icon")
        assert permission_icon.is_displayed()
