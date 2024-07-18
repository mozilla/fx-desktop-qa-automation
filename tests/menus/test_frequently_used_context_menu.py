import platform
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Devtools, Navigation
from modules.page_object import ExamplePage
from modules.util import BrowserActions, Utilities


@pytest.mark.unstable
def test_save_page_as(driver: Firefox):
    """
    C2637623.1: save page as
    """
    try:
        from pynput.keyboard import Key
    except ModuleNotFoundError:
        pytest.skip("Could not load pynput")
    # create objects
    context_menu = ContextMenu(driver)
    driver.get("https://example.com")
    example_page = ExamplePage(driver)
    nav = Navigation(driver)
    util = Utilities()
    ba = BrowserActions(driver)

    # right click something that is not a hyperlink
    title_header = example_page.get_element("title-header")
    example_page.context_click(title_header)

    context_menu.click_and_hide_menu("context-menu-save-page-as")

    downloads_button = nav.get_download_button()

    # short sleep to ensure menu is shown
    sleep(0.5)

    # perform key presses to save the file
    this_platform = platform.system()
    if this_platform == "Linux":
        ba.controller.press(Key.alt)
        ba.controller.press(Key.tab)
        ba.controller.release(Key.tab)
        ba.controller.release(Key.alt)

        ba.controller.press(Key.alt)
        ba.controller.press(Key.tab)
        ba.controller.release(Key.tab)
        ba.controller.release(Key.alt)

        ba.key_press_release(Key.tab)

        ba.key_press_release(Key.tab)

    # Press and release the Enter key
    ba.key_press_release(Key.enter)

    # Wait for the animation to complete
    nav.wait_for_download_animation_finish(downloads_button)

    # verify and delete downloaded file
    saved_image_location = util.get_saved_file_path("Example Domain.html")
    util.check_file_path_validility(saved_image_location)
    util.remove_file(saved_image_location)


def test_take_screenshot(driver: Firefox):
    """
    C2637623.2: take screenshot works from context menu
    """
    # create objects
    context_menu = ContextMenu(driver)
    driver.get("https://example.com")
    example_page = ExamplePage(driver)

    # ensure that the screenshot is not present
    example_page.element_does_not_exist("take-screenshot-box")

    # right click the header
    title_header = example_page.get_element("title-header")
    example_page.context_click(title_header)

    # context click the screenshot option and verify its not hidden
    context_menu.click_and_hide_menu("context-menu-take-screenshot")

    with driver.context(driver.CONTEXT_CHROME):
        screenshot_box = example_page.get_element("take-screenshot-box")
        assert screenshot_box.get_attribute("hidden") is None


def test_inspect(driver: Firefox):
    """
    C2637623.3: inspect works from context menu
    """
    # create objects
    context_menu = ContextMenu(driver)
    driver.get("https://example.com")
    example_page = ExamplePage(driver)
    devtools = Devtools(driver)

    # right click something that is not a hyperlink
    title_header = example_page.get_element("title-header")
    example_page.context_click(title_header)

    context_menu.click_and_hide_menu("context-menu-inspect")

    devtools.check_opened()
