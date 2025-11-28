import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar

TEST_URL = "https://example.com"
SITE_HOST = "example.com"


@pytest.fixture()
def test_case():
    return "3028949"


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

    # Step 4: Click "Switch to Tab" suggestion
    nav.click_switch_to_tab()

    # Step 5: Wait until only one tab remains
    tabs.wait_for_num_tabs(1)

    # Step 6: Reattach driver to the remaining tab
    handle = driver.window_handles[0]
    driver.switch_to.window(handle)

    # Step 7: Verify the remaining tab is the original TEST_URL
    assert TEST_URL in driver.current_url
