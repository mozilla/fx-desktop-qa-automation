import pytest
from pynput.keyboard import Controller
from selenium.webdriver import Firefox

from modules.page_object import Navigation, GenericPage


@pytest.fixture()
def test_case():
    return "464474"

@pytest.fixture()
def set_prefs():
    """Set prefs"""
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
            "groups": []
        },
        "matching": {
            "selectorData": "matching",
            "strategy": "id",
            "groups": []
        },
        "image-to-copy": {
            "selectorData": '/html/body/div[3]/div/div/section[2]/div/main/article/section/p[6]/img',
            "strategy": "xpath",
            "groups": []
        },
        "paragraph1": {
            "selectorData": '/html/body/div[3]/div/div/section[2]/div/main/article/section/p[1]',
            "strategy": "xpath",
            "groups": []
        },
        "paragraph2": {
            "selectorData": '/html/body/div[3]/div/div/section[2]/div/main/article/section/p[2]',
            "strategy": "xpath",
            "groups": []
        }
    }


DEMO_URL = "https://mystor.github.io/dragndrop/#"
COPY_URL = "https://1stwebdesigner.com/image-file-types/"

@pytest.mark.headed
@pytest.mark.xfail # a pref needs to be set only on windows, it was reported on bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1857764
def test_paste_image_text(driver: Firefox, sys_platform, temp_selectors):
    """
    C464474: Verify that pasting images and text from html works
    """
    # Initializing objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=DEMO_URL).open()
    web_page.elements |= temp_selectors
    keyboard = Controller()

    # Test pasting image data
    web_page.click_on("paste-image-data")

    # Copy an image from another website
    driver.switch_to.new_window("tab")
    nav.search(COPY_URL)
    web_page.element_exists("image-to-copy")
    web_page.copy_image_from_element(keyboard, "image-to-copy")

    # Paste it in the test area
    driver.switch_to.window(driver.window_handles[0])
    web_page.paste_to_element(sys_platform, "drop-area")
    web_page.element_attribute_contains("matching", "outerHTML", "green")

    # Test pasting text data
    web_page.click_on("paste-html-data")

    # Copy some text from another website
    driver.switch_to.window(driver.window_handles[1])
    web_page.scroll_to_element("paragraph1")
    start_element = web_page.get_element("paragraph1")
    end_element = web_page.get_element("paragraph2")
    web_page.actions.click_and_hold(start_element).move_to_element(end_element).release().perform()
    web_page.copy_selection(keyboard, "paragraph1")

    # Paste it in the test area
    driver.switch_to.window(driver.window_handles[0])
    web_page.paste_to_element(sys_platform, "drop-area")
    web_page.element_attribute_contains("matching", "outerHTML", "green")
