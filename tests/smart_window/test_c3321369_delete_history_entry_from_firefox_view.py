"""
C3321369 - Verify that the user can delete single History entries from the Firefox View page
"""

import pytest
from auto_fxui.browser_object import SmartWindow, TabBar
from auto_fxui.page_object_firefox_view import FirefoxView
from selenium.webdriver import Firefox

PAGES = ["lasagna.html", "flights.html", "museums.html"]


@pytest.fixture()
def test_case():
    return "3321369"


def test_delete_history_entry_from_firefox_view(
    driver: Firefox, active_smart_window: SmartWindow, tab_pages
):
    """
    C3321369 - Verify that the user can delete single History entries from the Firefox View page
    """
    urls = tab_pages(PAGES)
    deleted, kept = urls[1], [urls[0], urls[2]]
    TabBar(driver).open_urls_in_tabs(urls, open_first_in_current_tab=True)

    fx_view = FirefoxView(driver)
    fx_view.open_history()
    fx_view.expect_history_urls(urls)

    fx_view.delete_history_entry(deleted)
    fx_view.expect_history_url_gone(deleted)
    assert set(kept).issubset(fx_view.get_history_urls())
