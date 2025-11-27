import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar

TEST_URL = "https://example.com"
SITE_HOST = "example.com"


@pytest.fixture()
def test_case():
    return "3028949"


@pytest.mark.functional
def test_switch_to_existing_tab_when_having_the_same_URL(driver: Firefox):
    """
    3028949 - Handle switch to tab functionality
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Step 1: Open the first website
    driver.get(TEST_URL)

    # Step 2: Open a new tab and switch to it
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()

    # Step 3: Type same URL into Awesome Bar
    nav.clear_awesome_bar()
    nav.type_in_awesome_bar(SITE_HOST)

    # Step 4–5: Find AND CLICK "Switch to Tab" in chrome context
    with driver.context(driver.CONTEXT_CHROME):
        nav.wait.until(lambda d: len(nav.get_elements("switch-to-tab")) > 0)
        switch_row = nav.get_elements("switch-to-tab")[0]
        switch_row.click()

    # Step 6: After clicking, the new tab's context is discarded.
    # Re-attach to the remaining tab and assert we only have one.
    tabs.wait_for_num_tabs(1)
    remaining_handles = driver.window_handles
    assert len(remaining_handles) == 1

    driver.switch_to.window(remaining_handles[0])
    assert TEST_URL in driver.current_url
