import logging
import pytest

from selenium.webdriver import Firefox
from modules.page_object_generics import GenericPage
from modules.page_object import AboutPrefs
from modules.browser_object import TabBar

@pytest.fixture()
def test_case():
    return "545730"

def test_default_zoom_across_tabs(driver: Firefox):
    """
    This test verifies that the default zoom level is correctly set to 150%
    and persists across multiple tabs.
    """

    # Step 1: Open the browser and navigate to about:preferences
    about_prefs = AboutPrefs(driver, category="general").open()

    # Step 2: Set the default zoom level to 150%
    about_prefs.set_default_zoom(150)

    # Step 3: Open three tabs of the same website
    tabs = TabBar(driver)
    test_url = "https://www.example.com"

    # Open the first tab and load the URL
    page = GenericPage(driver, url=test_url)
    page.open()


    # Open two additional tabs
    for _ in range(2):
        tabs.new_tab_by_button()
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the newly opened tab
        page = GenericPage(driver, url=test_url)
        page.open()

    # Step 4: Verify the default zoom level in each tab
    for index, handle in enumerate(driver.window_handles, start=1):
        driver.switch_to.window(handle)

        # Verify the default zoom level
        with driver.context(driver.CONTEXT_CHROME):
            zoom_level_indicator = about_prefs.get_element("toolbar-zoom-level")
            zoom_level = zoom_level_indicator.get_attribute("label")
            logging.info(f"Zoom level in tab {index}: {zoom_level}")

            assert zoom_level == "150%", f"Default zoom level in tab {index} is {zoom_level}, expected '150%'"
