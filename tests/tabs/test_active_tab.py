import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar


NUM_TABS = 5

@pytest.fixture()
def test_case():
    return "134646"


@pytest.mark.ci
def test_active_tab(driver: Firefox):
    """
    C134646, ensures that the selected tab is highlighted
    """

    # Instantiate objects
    tabs = TabBar(driver)

    # Open 5 tabs
    for i in range(NUM_TABS):
        tabs.new_tab_by_button()

    # Go through all the tabs and ensure the focus is correct
    for i in range(1, NUM_TABS + 2):
        with driver.context(driver.CONTEXT_CHROME):
            target_tab = tabs.get_tab(i)
            target_tab.click()
            tabs.custom_wait(timeout=3).until(
                lambda d: target_tab.get_attribute("visuallyselected") == ""
            )
