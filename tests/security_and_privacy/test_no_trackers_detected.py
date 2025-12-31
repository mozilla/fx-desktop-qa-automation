import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation


@pytest.fixture()
def test_case():
    return "446391"


NOTRACKERS_URL = "http://example.com/"


def test_no_trackers_detected(driver: Firefox, nav: Navigation):
    """
    C446391 No trackers are detected
    """
    # access url
    driver.get(NOTRACKERS_URL)
    # verify that no trackers are detected
    # no list of trackers is displayed
    nav.assert_blocked_trackers()
