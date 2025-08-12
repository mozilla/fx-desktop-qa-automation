import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar


@pytest.fixture()
def test_case():
    return "134646"


@pytest.mark.ci
def test_active_tab(driver: Firefox):
    """
    C134646, ensures that the selected tab is highlighted
    """
    tabs = TabBar(driver)
    num_tabs = 5

    # Open 5 tabs
    for i in range(num_tabs):
        tabs.new_tab_by_button()

    # Go through all the tabs and ensure the focus is correct
    for i in range(1, num_tabs + 2):
        with driver.context(driver.CONTEXT_CHROME):
            target_tab = tabs.get_tab(i)
            target_tab.click()
            tabs.custom_wait(timeout=3).until(
                lambda d: target_tab.get_attribute("visuallyselected") == ""
            )
