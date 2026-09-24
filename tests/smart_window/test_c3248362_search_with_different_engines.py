"""
C3248362 - Search with different engines
Verify picking a non-default engine from the Smart Bar's Search With submenu
sends the query to that engine.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartBar, SmartWindow

QUERY = "kangaroo"
# Bing rather than the default: it is offered in every locale this runs in and,
# unlike Google, does not serve a bot interstitial under automation, so the
# landing URL is the real search URL.
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

    # The submenu holds only a generic "Search" entry until the search service
    # finishes initialising; a Windows CI worker read exactly that and failed.
    bar.expect_search_engines()

    available = bar.get_search_with_items()
    assert ENGINE in available, (
        f"{ENGINE} missing from the Search With submenu: {available}"
    )

    # Choosing an engine only sets it; Enter runs the search. The choice is not
    # reflected in any CTA attribute, so the URL is the only assertable proof.
    bar.choose_search_engine(ENGINE)
    bar.submit()

    active_smart_window.expect_selected_tab_url_contains(ENGINE_HOST)
    active_smart_window.expect_selected_tab_url_contains(QUERY)
