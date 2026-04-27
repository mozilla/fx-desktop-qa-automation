import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel


@pytest.fixture()
def test_case():
    return "3054032"


NOTRACKERS_URL = "https://example.com/"


def test_no_trackers_detected(driver: Firefox, trust_panel: TrustPanel):
    """
    C446391 No trackers are detected
    """
    # access url
    driver.get(NOTRACKERS_URL)
    # verify that no trackers are detected
    trust_panel.open_panel()
    trust_panel.assert_no_trackers()
