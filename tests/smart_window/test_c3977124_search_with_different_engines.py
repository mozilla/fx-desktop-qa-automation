"""
C3977124 - Search with different engines directly from the Smart Bar
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow
from selenium.webdriver import Firefox

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

    # Both reads race the search service initialising.
    bar.expect_default_search_engine()
    default_engine = bar.get_default_search_engine()
    bar.expect_search_engines()
    engines = bar.get_search_with_items()

    other = next(e for e in engines if e != default_engine)
    bar.choose_search_engine(other)

    # Checked before submitting: the search navigates away afterwards.
    assert bar.get_default_search_engine() == default_engine, (
        f"default engine changed from {default_engine!r} after choosing {other!r}"
    )

    bar.submit()
    active_smart_window.expect_selected_tab_url_contains(QUERY)
