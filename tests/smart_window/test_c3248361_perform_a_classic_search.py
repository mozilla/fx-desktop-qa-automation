"""
C3248361 - Perform a Classic Search
Verify a query typed into the Smart Bar and submitted runs a search with the
default engine.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartBar, SmartWindow

QUERY = "kangaroo"


@pytest.fixture()
def test_case():
    return "3248361"


def test_perform_a_classic_search(driver: Firefox, active_smart_window: SmartWindow):
    """
    C3248361 - Perform a Classic Search
    """
    bar = SmartBar(driver)
    bar.open_smart_bar()
    bar.set_smart_bar_text(QUERY)
    bar.submit()

    # Assert the navigation, not the page. The default engine is Google, which
    # serves a bot interstitial under automation -- but that URL still carries
    # the search target and the query, so both checks hold either way.
    active_smart_window.expect_selected_tab_url_contains("google.com")
    active_smart_window.expect_selected_tab_url_contains(QUERY)
