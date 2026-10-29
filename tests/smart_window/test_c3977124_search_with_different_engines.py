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

    # Both reads race the search service: the CTA reports "" and the submenu
    # holds only a generic "Search" entry until it initialises.
    bar.expect_default_search_engine()
    default_engine = bar.get_default_search_engine()
    bar.expect_search_engines()
    engines = bar.get_search_with_items()
    assert len(engines) > 1, f"Search With offered only {engines}"

    # Search with an engine that is not the default, then confirm the default
    # itself did not change -- that is the part of the case worth asserting.
    other = next(e for e in engines if e != default_engine)
    bar.choose_search_engine(other)

    # The case's own wording: the default is a one-off override, so the CTA
    # must still name the original engine. Checked before submitting, since
    # the search navigates away and the bar is not reliably writable after.
    assert bar.get_default_search_engine() == default_engine, (
        f"default engine changed from {default_engine!r} after choosing {other!r}"
    )

    bar.submit()
    active_smart_window.expect_selected_tab_url_contains(QUERY)
