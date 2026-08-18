import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://edition.cnn.com/"
MAX_ATTEMPTS = 3


@pytest.fixture()
def test_case():
    return "3054033"


def test_see_all_link_redirects_to_blocked_trackers(
    driver: Firefox,
    trust_panel: TrustPanel,
):
    """
    C3054033 - “See all” link correctly redirects the user
    to the blocked trackers.
    """

    test_page = GenericPage(driver, url=TEST_URL)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            test_page.open()
            trust_panel.open_panel()
            trust_panel.wait_for_trackers()
            trust_panel.click_see_all()
            trust_panel.wait_for_tracker_sections()
            break
        except TimeoutException:
            if attempt == MAX_ATTEMPTS:
                raise
