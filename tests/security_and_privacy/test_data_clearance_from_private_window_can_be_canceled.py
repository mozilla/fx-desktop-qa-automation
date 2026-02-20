import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar


@pytest.fixture()
def test_case():
    return "2359314"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


URLS = ["https://facebook.com/", "https://www.youtube.com/"]


def test_data_clearance_from_private_window_can_be_canceled(driver: Firefox):
    """
    C2359314 - Verify that data clearance from a Private Window can be canceled
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Open a few websites to create some data
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)

    # Record the number of open window tabs
    num_open_tabs = len(driver.window_handles)

    # Click on the data clearance (End private session) button
    nav.click_on("end-private-session-button")

    # Verify the confirmation dialog is displayed
    nav.element_visible("delete-session-data-button")

    # Click the "Cancel" button
    nav.click_on("cancel-session-data-button")

    # Verify the end private session process is stopped and the previously open tabs are still displayed
    assert len(driver.window_handles) == num_open_tabs
    nav.url_contains(URLS[-1])

    # Click on the data clearance (End private session) button again
    nav.click_on("end-private-session-button")

    # Verify the confirmation dialog is displayed and the "Always ask me" checkbox is still checked
    nav.element_visible("delete-session-data-button")
    nav.element_attribute_contains("always-ask-pbm-checkbox", "checked", "true")
