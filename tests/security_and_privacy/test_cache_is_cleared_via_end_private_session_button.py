import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutCache


@pytest.fixture()
def test_case():
    return "2359320"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


URL = "https://edition.cnn.com/"
EXPECTED_CACHE_DOMAIN = "cnn"


def test_cache_is_cleared_via_end_private_session_button(driver: Firefox):
    """
    C2359320 - Verify that cache is cleared when "End Private Session" is used in a Private Window
    """
    # Instantiate objects
    about_cache = AboutCache(driver)
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")
    driver.get(URL)

    # Open a new tab and go to about:cache?storage=memory
    about_cache.open()
    about_cache.open_disk_or_memory_cache_entries("memory")

    # Verify CNN is in the memory cache entries
    entries_text = about_cache.get_entries_text()
    assert EXPECTED_CACHE_DOMAIN in entries_text

    # Click "End Private Session" and confirm "Delete session data"
    nav.end_private_session()

    # Go back to about:cache and assert memory cache has 0 entries
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_cache.open()

    num_entries = about_cache.get_number_of_entries()
    assert num_entries == "0"
