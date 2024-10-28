from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "65064"


TEST_PAGE = "https://en.wikipedia.org"


def test_zoom_menu_correlation(driver: Firefox):
    # Open a webpage to test zoom level

    page = GenericPage(driver, url=TEST_PAGE)
    sleep(1)

    # Open the Firefox Menu panel and prepare to interact with zoom controls
    panel = PanelUi(driver).open()
    panel.open_panel_menu()

    # Switch to Firefox's Chrome context for UI interaction
    # Step 1: Zoom out twice to approximately 90%
    panel.click_on("zoom-reduce")
    sleep(2)

    # Verify that the CSS zoom level reflects the 90% zoom out
    css_zoom = page.get_css_zoom()
    assert css_zoom == 0.9, f"Expected CSS zoom == 0.9, but got {css_zoom}"

    # Step 2: Reset zoom to 100%
    panel.click_on("zoom-reset")
    sleep(2)

    # Verify that the CSS zoom level is back to 1.0 (100%)
    css_zoom = page.get_css_zoom()
    assert css_zoom == 1.0, f"Expected CSS zoom of 1.0, but got {css_zoom}"

    # Step 2: Zoom in to approximately 110%
    panel.click_on("zoom-enlarge")
    sleep(2)

    # Verify that the CSS zoom level reflects the 110% zoom in
    css_zoom = page.get_css_zoom()
    assert css_zoom == 1.1, f"Expected CSS zoom == 1.1, but got {css_zoom}"
