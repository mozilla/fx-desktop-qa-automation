import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import TabBar


@pytest.fixture()
def test_case():
    return "134640"


URLS = [
    "about:about",
    "about:addons",
    "about:cache",
    "about:robots",
]


def test_reopen_tabs_through_keys(driver: Firefox, sys_platform: str):
    """
    C134640 - Verify that previously closed tabs can be reopened using
    the keyboard shortcut (Ctrl/Cmd + Shift + T).
    """

    # Instantiate object
    tabs = TabBar(driver)

    # Create 4 new tabs
    for i in range(4):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(URLS[i])
    assert len(driver.window_handles) == 5

    # Close 4 tabs
    for i in range(4):
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
    assert len(driver.window_handles) == 1

    # Use the refactored method to reopen tabs with shortcut
    tabs.reopen_tabs_with_shortcut(sys_platform, count=4)

    # Verify the correct tabs reopened (order is not considered)
    open_urls = set()

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        open_urls.add(driver.current_url)

    for url in URLS:
        assert url in open_urls, f"Expected reopened tab with URL '{url}' not found"
