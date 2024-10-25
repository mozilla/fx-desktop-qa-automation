import time
import pytest
from pynput.keyboard import Controller, Key
from selenium.webdriver import Firefox

from modules.page_object import Navigation, GenericPage


@pytest.fixture()
def test_case():
    return "464474"

@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


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
            "groups": []
        },
        "image-to-copy": {
            "selectorData": '//*[@id="post-42178"]/section/p[6]/img',
            "strategy": "xpath",
            "groups": []
        }
    }


DEMO_URL = "https://mystor.github.io/dragndrop/#"
COPY_URL = "https://1stwebdesigner.com/image-file-types/"

@pytest.mark.headed
def test_paste_image_text(driver: Firefox, temp_selectors):
    """
    C464474: Verify that pasting images and text from html works
    """
    # Initializing objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=DEMO_URL).open()
    web_page.elements |= temp_selectors
    keyboard = Controller()

    # Click button to start the test of pasting image data
    web_page.click_on("paste-image-data")

    # Copy an image from another website
    driver.switch_to.new_window("tab")
    nav.search(COPY_URL)
    time.sleep(3)
    web_page.copy_image(keyboard, "image-to-copy")

    time.sleep(15)