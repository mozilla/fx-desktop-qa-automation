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

    # Assert that the default search engine is set and get the default search engine
    bar.expect_default_search_engine()
    engine = bar.get_default_search_engine()

    bar.submit()

    # Assert that the search engine is in the URL and that the query is in the URL
    active_smart_window.expect_selected_tab_url_contains(engine.split()[0].lower())
    active_smart_window.expect_selected_tab_url_contains(QUERY)
