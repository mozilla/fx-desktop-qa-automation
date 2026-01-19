import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object_firefox_view import FirefoxView


@pytest.fixture()
def test_case():
    return "2333476"


TEST_URLS = [
    "about:about",
    "about:mozilla",
    "about:robots",
]


def test_fx_view_closed_tabs_from_multiple_windows_shown_in_recently_closed_section(
    driver: Firefox,
):
    """
    C2333476 - Verify that closed tabs from multiple windows are shown in Fx View Recently closed section.
    """
    tabs = TabBar(driver)
    fx_view = FirefoxView(driver)

    # Open a few random web pages in different tabs
    tabs.open_multiple_tabs_with_pages(TEST_URLS)

    # Close the last two tabs
    num_tabs = len(driver.window_handles)
    for i in range(2):
        tab = tabs.get_tab(num_tabs - i)
        assert tab is not None
        tabs.close_tab(tab)

    # Switch to the first window handle
    driver.switch_to.window(driver.window_handles[0])

    # Navigate to Firefox View Recently Closed section
    fx_view.open_recently_closed_section()

    # Verify that closed tabs are shown in Recently Closed section
    expected_closed_urls = set(TEST_URLS[-2:])
    fx_view.wait.until(
        lambda _: set(fx_view.get_recently_closed_tab_urls()) == expected_closed_urls
    )
    actual_closed_urls = set(fx_view.get_recently_closed_tab_urls())
    assert actual_closed_urls == expected_closed_urls
