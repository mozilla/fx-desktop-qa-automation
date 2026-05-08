import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPage

WIKI_IMAGE_URL = (
    "https://en.wikipedia.org/wiki/Firefox#/media/File:Firefox_logo,_2019.svg"
)


@pytest.fixture()
def test_case():
    return "0"


def test_debug_contextmenu_visual(driver: Firefox):
    """Debug test to verify the contextmenu_visual flow opens a new tab with Google Lens."""
    wiki_page = GenericPage(driver, url=WIKI_IMAGE_URL)
    context_menu = ContextMenu(driver)

    wiki_page.open()
    wiki_page.wait_for_page_to_load()

    image = wiki_page.get_element("mediawiki-image")
    wiki_page.context_click(image)
    context_menu.click_and_hide_menu("context-menu-search-image-with-lens")

    # Print number of tabs and current URL to verify a new tab opened
    print(f"\nNumber of tabs: {len(driver.window_handles)}")
    driver.switch_to.window(driver.window_handles[-1])
    print(f"URL opened: {driver.current_url}")

    assert len(driver.window_handles) > 1, "No new tab was opened by Google Lens search"
