import pytest
from selenium.common import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "122611"


TEST_URL = "https://www.w3schools.com/html/html5_geolocation.asp"


def test_geolocation_prompt_is_triggered_on_request_location_on_website(
    driver: Firefox,
):
    """
    C122611 - Verify that geolocation prompt is present when accessing a website that requests location
    """

    # Instantiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()

    # Wait for the page to fully load and manually address the cookie banner if appears, as the cookie banner
    # dismissal preference is not effective in this context
    nav.wait_for_page_to_load()
    try:
        driver.switch_to.window(driver.window_handles[-1])
        web_page.find_element(By.ID, "accept-choices").click()
    except NoSuchElementException:
        # If the banner is not triggered, just continue to the next line
        pass

    # Click the 'Try It' button to trigger the geolocation prompt
    web_page.find_element(
        By.CSS_SELECTOR, "button.w3-btn.w3-blue.w3-round[onclick='getLocation()']"
    ).click()

    # Verify that the geolocation prompt is present
    assert nav.wait.until(
        lambda _: nav.element_visible("geolocation-notification-container")
    ), "Geolocation prompt did not appear within the expected time"
