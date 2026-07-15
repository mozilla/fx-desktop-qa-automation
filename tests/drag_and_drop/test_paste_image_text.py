import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu
from modules.page_object import GenericPage, Navigation


@pytest.fixture()
def test_case():
    return "464474"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("clipboard.imageAsFile.enabled", False)]


@pytest.fixture()
def temp_selectors():
    return {
        "paste-image-data": {
            "selectorData": "#testlist > li:nth-child(11) > a:nth-child(1)",
            "strategy": "css",
            "groups": [],
        },
        "paste-html-data": {
            "selectorData": "#testlist > li:nth-child(12) > a:nth-child(1)",
            "strategy": "css",
            "groups": [],
        },
        "drop-area": {
            "selectorData": "#droparea",
            "strategy": "css",
            "groups": ["doNotCache"],
        },
        "matching": {
            "selectorData": "matching",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "image-to-copy": {
            "selectorData": ".m24-c-donate-media > img",
            "strategy": "css",
            "groups": [],
        },
        "paragraph1": {
            "selectorData": ".m24-c-donate-body > p:nth-of-type(1)",
            "strategy": "css",
            "groups": [],
        },
    }


DEMO_URL = "https://mystor.github.io/dragndrop/#"
COPY_URL = "https://www.mozilla.org/en-US"


@pytest.mark.headed
def test_paste_image_text(driver: Firefox, sys_platform, temp_selectors):
    """
    C464474: Verify that pasting images and text from html works
    """
    # Initializing objects
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    web_page = GenericPage(driver, url=DEMO_URL).open()
    web_page.elements |= temp_selectors

    # Test pasting image data
    web_page.click_on("paste-image-data")

    # Copy an image from another website via its context menu
    driver.switch_to.new_window("tab")
    nav.search(COPY_URL)
    web_page.element_exists("image-to-copy")
    web_page.scroll_to_element("image-to-copy")
    web_page.context_click("image-to-copy")
    context_menu.click_and_hide_menu("context-menu-copy-image")

    # Paste it in the test area
    driver.switch_to.window(driver.window_handles[0])
    web_page.paste_to_element(sys_platform, "drop-area")
    web_page.element_attribute_contains("matching", "outerHTML", "green")

    # Test pasting text data
    web_page.click_on("paste-html-data")

    # Copy some text from another website via its context menu
    driver.switch_to.window(driver.window_handles[1])
    web_page.scroll_to_element("paragraph1")
    web_page.triple_click("paragraph1")
    web_page.context_click("paragraph1")
    context_menu.click_and_hide_menu("context-menu-copy")

    # Paste it in the test area
    driver.switch_to.window(driver.window_handles[0])
    web_page.paste_to_element(sys_platform, "drop-area")
    web_page.element_attribute_contains("matching", "outerHTML", "green")
