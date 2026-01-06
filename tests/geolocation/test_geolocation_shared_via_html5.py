import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, TabBar
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "15189"


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
    return "https://browserleaks.com/geo"


# Test is unstable on Windows GHA because of permission changes on the CI image
def test_allow_permission_on_geolocation_via_html5(
    driver: Firefox,
    nav: Navigation,
    tabs: TabBar,
    test_url: str,
    generic_page: GenericPage,
):
    """
    C15189 - Verify that geolocation is successfully shared when the user allows permission via the HTML5 Geolocation API
    """
    # Instantiate Objects
    generic_page.open()

    # Allow the location sharing
    nav.handle_geolocation_prompt(button_type="primary")

    # Check that the latitude and longitude are displayed
    generic_page.wait_for_geolocation_data()

    # Allow the location sharing while choose the option Remember this decision
    tabs.open_single_page_in_new_tab(generic_page, num_tabs=2)
    nav.click_on("checkbox-remember-this-decision")
    nav.handle_geolocation_prompt(button_type="primary")

    # Check that the latitude and longitude are displayed
    generic_page.wait_for_geolocation_data()

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
):
    """
    C15189 - Verify that geolocation is not shared when the user blocks permission via the HTML5 Geolocation API
    """
    # Instantiate Objects
    generic_page.open()

    # Block the location sharing
    nav.handle_geolocation_prompt(button_type="secondary")

    # Check that the location is not shared, a warning message is displayed
    warning_element = generic_page.find_element(By.ID, "geo-warn")
    assert (
        "PERMISSION_DENIED – User denied Geolocation"
        in warning_element.get_attribute("innerHTML")
    )

    # Block the location sharing while choose the option Remember this decision
    tabs.open_single_page_in_new_tab(generic_page, num_tabs=2)
    nav.click_on("checkbox-remember-this-decision")
    nav.handle_geolocation_prompt(button_type="secondary")

    # Check that the location is not shared, a warning message is displayed
    warning_element = generic_page.find_element(By.ID, "geo-warn")
    assert (
        "PERMISSION_DENIED – User denied Geolocation"
        in warning_element.get_attribute("innerHTML")
    )

    # Assert that the permission icon is displayed in address bar when in a new tab
    tabs.open_single_page_in_new_tab(generic_page, num_tabs=3)
    nav.expect_in_chrome(
        lambda _: nav.get_element("permissions-location-icon").is_displayed()
    )
