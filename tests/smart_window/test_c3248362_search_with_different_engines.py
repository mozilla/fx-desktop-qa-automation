"""
C3248362 - Search with different engines
Verify picking a non-default engine from the Search With submenu sends the
query to that engine.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartBar, SmartWindow

QUERY = "kangaroo"
ENGINE = "Bing"
ENGINE_HOST = "bing.com"


@pytest.fixture()
def test_case():
    return "3248362"


def test_search_with_different_engines(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C3248362 - Search with different engines
    """
    bar = SmartBar(driver)
    bar.open_smart_bar()
    bar.set_smart_bar_text(QUERY)

    bar.expect_search_engine_offered(ENGINE)
    bar.choose_search_engine(ENGINE)
    # Choosing only sets the engine; Enter runs the search.
    bar.submit()

    active_smart_window.expect_selected_tab_url_contains(ENGINE_HOST)
    active_smart_window.expect_selected_tab_url_contains(QUERY)
