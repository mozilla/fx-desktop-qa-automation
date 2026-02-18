import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar


@pytest.fixture()
def test_case():
    return "2186610"


URLS = [
    "about:about",
    "about:mozilla",
    "about:logo",
    "about:robots",
]


def test_restore_closed_tabs(driver: Firefox, tabs: TabBar, sys_platform: str):
    """
    C2186610 - Verify that the last closed tab is restored by keyboard shortcut (Ctrl/Cmd + Shift + T).
    """
    # First tab must not be blank page (otherwise we get restore tab into that blank tab)
    driver.get(URLS[1])

    # Open a new tab, close that tab, then restore it
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(URLS[3])
    assert tabs.wait_for_num_tabs(2)
    driver.close()
    assert tabs.wait_for_num_tabs(1)
    tabs.reopen_tabs_with_shortcut(sys_platform, count=1)
    assert tabs.wait_for_num_tabs(2)

    # Clean up for next steps
    driver.switch_to.window(driver.window_handles[-1])
    driver.close()

    # Open 4 new tabs
    for i in range(4):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(URLS[i])
    assert tabs.wait_for_num_tabs(5)

    # Close those 4 tabs
    for i in range(4):
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])
    assert tabs.wait_for_num_tabs(1)

    # Use the method to restore the closed tabs with shortcut
    tabs.reopen_tabs_with_shortcut(sys_platform, count=4)
    assert tabs.wait_for_num_tabs(5)

    # Verify the page of each tab was restored
    open_urls = set()
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        open_urls.add(driver.current_url)

    for url in URLS:
        assert url in open_urls, f"Expected reopened tab with URL '{url}' not found"
