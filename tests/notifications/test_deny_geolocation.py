import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "122613"


@pytest.fixture()
def temp_selectors():
    return {"not-allowed": {"selectorData": "geo-warn", "strategy": "id", "groups": []}}


TEST_URL = "https://browserleaks.com/geo"


def test_deny_geolocation(driver: Firefox, web_page):
    """
    C122613 - Verify that denying geolocation permissions prevents website from accessing the location
    """
    # Instantiate Objects
    nav = Navigation(driver)
    page = web_page(TEST_URL)

    # Block geolocation sharing for this website
    nav.element_clickable("popup-notification-secondary-button")
    nav.click_on("popup-notification-secondary-button")

    # Check that the website cannot access the geolocation
    page.element_visible("not-allowed")
    assert "PERMISSION_DENIED – User denied Geolocation" in page.get_element(
        "not-allowed"
    ).get_attribute("innerHTML")
