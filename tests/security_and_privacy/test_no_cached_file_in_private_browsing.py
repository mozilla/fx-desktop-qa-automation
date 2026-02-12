import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutCache


@pytest.fixture()
def test_case():
    return "101678"


def test_no_cached_file_in_private_browsing(driver: Firefox, panel_ui, websites):
    """
    C101678: Verify that no cached files are stored when browsing in a Private Window.
    """
    about_cache = AboutCache(driver)

    # Open a private window and switch to it
    panel_ui.open_and_switch_to_new_window("private")

    # Visit several websites in Private Browsing
    for url in websites:
        driver.get(url)

    # Go to about:cache overview
    about_cache.open()

    # Open the disk cache entries list
    about_cache.open_disk_or_memory_cache_entries("disk")

    # Get all cache entries text and verify visited sites are not present
    entries_text = about_cache.get_entries_text()

    for url in websites:
        assert url not in entries_text, (
            f"Found private-browsing URL in cache entries: {url}"
        )
