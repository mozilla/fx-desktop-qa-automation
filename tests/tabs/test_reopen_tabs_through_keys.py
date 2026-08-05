import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar

URLS = (
    "about:about",
    "about:addons",
    "about:cache",
    "about:robots",
)

ORIGINAL_URL = "about:mozilla"


@pytest.fixture()
def test_case():
    return "134640"


def test_reopen_tabs_through_keys(driver: Firefox, sys_platform: str):
    """
    C134640 - Verify that previously closed tabs can be reopened using
    the keyboard shortcut (Ctrl/Cmd + Shift + T).
    """
    tabs = TabBar(driver)

    # Prevent Firefox from restoring the first closed tab into an existing
    # blank new tab without creating a new window handle.
    driver.get(ORIGINAL_URL)
    tabs.url_contains(ORIGINAL_URL)

    original_handle = driver.current_window_handle
    opened_handles = []

    for expected_tab_count, url in enumerate(URLS, start=2):
        handles_before = set(driver.window_handles)

        tabs.new_tab_by_button()
        tabs.wait_for_num_tabs(expected_tab_count)

        new_handles = set(driver.window_handles) - handles_before
        assert len(new_handles) == 1, (
            f"Expected exactly one new tab, but found: {new_handles}"
        )

        new_handle = new_handles.pop()
        opened_handles.append(new_handle)

        driver.switch_to.window(new_handle)
        driver.get(url)
        tabs.url_contains(url)

    # Close only the tabs created by this test, newest first.
    for expected_tab_count, handle in zip(
        range(len(URLS), 0, -1),
        reversed(opened_handles),
        strict=True,
    ):
        driver.switch_to.window(handle)
        driver.close()
        tabs.wait_for_num_tabs(expected_tab_count)

    driver.switch_to.window(original_handle)

    reopened_handles = []

    # Restore and wait for one tab at a time to avoid racing Firefox.
    for expected_tab_count in range(2, len(URLS) + 2):
        handles_before = set(driver.window_handles)

        tabs.reopen_tabs_with_shortcut(count=1)
        tabs.wait_for_num_tabs(expected_tab_count)

        new_handles = set(driver.window_handles) - handles_before
        assert len(new_handles) == 1, (
            f"Expected exactly one tab to reopen, but found: {new_handles}"
        )

        reopened_handles.append(new_handles.pop())

    reopened_urls = set()

    for handle in reopened_handles:
        driver.switch_to.window(handle)
        tabs.expect_in_content(lambda d: d.current_url in URLS)
        reopened_urls.add(driver.current_url)

    assert reopened_urls == set(URLS), (
        f"Expected reopened URLs {set(URLS)}, but found {reopened_urls}"
    )
