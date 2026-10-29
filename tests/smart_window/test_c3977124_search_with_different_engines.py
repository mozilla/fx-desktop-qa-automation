"""
C3977124 - Search with different engines directly from the Smart Bar
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartBar, SmartWindow

QUERY = "test"


@pytest.fixture()
def test_case():
    return "3977124"


def test_search_with_different_engines(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C3977124 - Search with different engines directly from the Smart Bar
    """
    bar = SmartBar(driver)
    bar.open_smart_bar()
    bar.set_smart_bar_text(QUERY)

    default_engine = bar.get_default_search_engine()
    engines = bar.get_search_with_items()
    assert len(engines) > 1, f"Search With offered only {engines}"

    # Search with an engine that is not the default, then confirm the default
    # itself did not change -- that is the part of the case worth asserting.
    other = next(e for e in engines if e != default_engine)
    bar.choose_search_engine(other)
    bar.submit()
    active_smart_window.expect_selected_tab_url_contains(QUERY)

    bar.open_smart_bar()
    bar.set_smart_bar_text(QUERY)
    assert bar.get_default_search_engine() == default_engine, (
        f"default engine changed from {default_engine!r} after searching with {other!r}"
    )
