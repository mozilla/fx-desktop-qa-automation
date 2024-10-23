import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, TabBar
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "15189"


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


TEST_URL = "https://browserleaks.com/geo"


def wait_for_geolocation_data(web_page, timeout=20):
    """Wait until both latitude and longitude data are available."""
    web_page.custom_wait(timeout=timeout).until(
        lambda _: all([
            web_page.find_element(By.ID, "latitude").get_attribute("data-raw") is not None,
            web_page.find_element(By.ID, "longitude").get_attribute("data-raw") is not None
        ])
    )


def test_allow_permission_on_geolocation_via_html5(driver: Firefox):
    """
    C15189 - Verify that geolocation is successfully shared when the user allows permission via the HTML5 Geolocation API
    """
    # Instantiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    tabs = TabBar(driver)

    # Allow the location sharing
    nav.handle_geolocation_prompt(button_type="primary")

    # Check that the latitude and longitude are displayed
    wait_for_geolocation_data(web_page)

    # Allow the location sharing while choose the option Remember this decision
    tabs.open_web_page_in_new_tab(web_page, num_tabs=2)
    nav.element_clickable("checkbox-remember-this-decision")
    nav.click_on("checkbox-remember-this-decision")
    nav.handle_geolocation_prompt(button_type="primary")

    # Check that the latitude and longitude are displayed
    wait_for_geolocation_data(web_page)

    # Assert that the permission icon is displayed in address bar when in a new tab
    tabs.open_web_page_in_new_tab(web_page, num_tabs=3)
    with driver.context(driver.CONTEXT_CHROME):
        permission_icon = nav.get_element("permissions-location-icon")
        assert permission_icon.is_displayed()


def test_block_permission_on_geolocation_via_w3c_api(driver: Firefox):
    """
    C15189 - Verify that geolocation is not shared when the user blocks permission via the HTML5 Geolocation API
    """
    # Instantiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    tabs = TabBar(driver)

    # Block the location sharing
    nav.handle_geolocation_prompt(button_type="secondary")

    # Check that the location is not shared, a warning message is displayed
    warning_element = web_page.find_element(By.ID, "geo-warn")
    assert "PERMISSION_DENIED – User denied Geolocation" in warning_element.get_attribute("innerHTML")

    # Block the location sharing while choose the option Remember this decision
    nav.refresh_page()
    nav.element_clickable("checkbox-remember-this-decision")
    nav.click_on("checkbox-remember-this-decision")
    nav.handle_geolocation_prompt(button_type="secondary")

    # Check that the location is not shared, a warning message is displayed
    warning_element = web_page.find_element(By.ID, "geo-warn")
    assert "PERMISSION_DENIED – User denied Geolocation" in warning_element.get_attribute("innerHTML")

    # Assert that the permission icon is displayed in address bar when in a new tab
    tabs.open_web_page_in_new_tab(web_page, num_tabs=2)
    with driver.context(driver.CONTEXT_CHROME):
        permission_icon = nav.get_element("permissions-location-icon")
        assert permission_icon.is_displayed()