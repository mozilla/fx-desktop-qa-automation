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

COOKIE_ACCEPT_BUTTON = (By.ID, "accept-choices")

TRY_IT_BUTTON = (
    By.CSS_SELECTOR,
    "button.w3-btn.w3-blue.w3-round[onclick='getLocation()']",
)


def _switch_to_latest_window(driver: Firefox) -> None:
    """
    Switches WebDriver focus to the most recently opened window/tab.
    """
    handles = driver.window_handles
    if handles:
        driver.switch_to.window(handles[-1])


def _dismiss_cookie_banner_if_present(driver: Firefox, page: GenericPage) -> None:
    """
    Dismisses the cookie banner if present. No-ops if not found.
    """
    _switch_to_latest_window(driver)
    try:
        page.find_element(*COOKIE_ACCEPT_BUTTON).click()
    except NoSuchElementException:
        return


def test_geolocation_prompt_is_triggered_on_request_location_on_a_website(
    driver: Firefox,
):
    """
    C122611 - Verify that geolocation prompt is present when accessing a website that requests location
    """

    nav = Navigation(driver)
    page = GenericPage(driver, url=TEST_URL).open()

    _dismiss_cookie_banner_if_present(driver, page)
    page.find_element(*TRY_IT_BUTTON).click()

    nav.wait.until(lambda _: nav.element_visible("geolocation-notification-container"))
