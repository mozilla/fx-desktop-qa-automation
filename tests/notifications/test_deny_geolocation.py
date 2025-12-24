import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "122613"


@pytest.fixture()
def temp_selectors():
    return {"not-allowed": {"selectorData": "geo-warn", "strategy": "id", "groups": []}}


@pytest.fixture()
def web_page(driver: Firefox, temp_selectors):
    page = GenericPage(driver, url=TEST_URL).open()
    page.elements |= temp_selectors
    return page


TEST_URL = "https://browserleaks.com/geo"


def test_deny_geolocation(driver: Firefox, web_page):
    """
    C122613 - Verify that denying geolocation permissions prevents website from accessing the location
    """
    # Instatiate Objects
    nav = Navigation(driver)

    # Block geolocation sharing for this website
    nav.element_clickable("popup-notification-secondary-button")
    nav.click_on("popup-notification-secondary-button")

    # Check that the website cannot access the geolocation
    web_page.element_visible("not-allowed")
    assert "PERMISSION_DENIED – User denied Geolocation" in web_page.get_element(
        "not-allowed"
    ).get_attribute("innerHTML")
