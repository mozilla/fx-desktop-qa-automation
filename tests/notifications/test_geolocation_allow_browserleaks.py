import pytest

from modules.browser_object import Navigation
from modules.page_object import GenericPage


TEST_URL = "https://browserleaks.com/geo"


@pytest.fixture()
def test_case():
    return "122612"


def test_geolocation_allow_browserleaks(driver):
    """
    C122612 - Verify geolocation prompt is displayed on BrowserLeaks and Allow grants permission.
    """
    nav = Navigation(driver)
    page = GenericPage(driver, url=TEST_URL)
    page.open()

    # Prompt is displayed
    nav.wait.until(lambda _: nav.element_visible("geolocation-notification-container"))

    # Allow permission
    nav.handle_geolocation_prompt(button_type="primary", remember_this_decision=False)

    # Permission indicator is shown in the address bar
    nav.expect_in_chrome(lambda _: nav.get_element("permissions-location-icon").is_displayed())
