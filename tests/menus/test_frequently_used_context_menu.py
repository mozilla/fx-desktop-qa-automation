import platform
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
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
    context_menu.context_click_element(title_header)

    with driver.context(driver.CONTEXT_CHROME):
        save_page_as = context_menu.get_context_item("context-menu-save-page-as")
        save_page_as.click()

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
    with driver.context(driver.CONTEXT_CHROME):
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
    with driver.context(driver.CONTEXT_CHROME):
        example_page.element_does_not_exist("take-screenshot-box")

    # right click the header
    title_header = example_page.get_element("title-header")
    context_menu.context_click_element(title_header)

    # context click the screenshot option and verify its not hidden
    with driver.context(driver.CONTEXT_CHROME):
        take_screenshot = context_menu.get_context_item("context-menu-take-screenshot")
        take_screenshot.click()
        context_menu.hide_popup_by_child_node(take_screenshot)

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

    # right click something that is not a hyperlink
    title_header = example_page.get_element("title-header")
    context_menu.context_click_element(title_header)

    # find an element present in the dev tools
    with driver.context(driver.CONTEXT_CHROME):
        inspect_option = context_menu.get_context_item("context-menu-inspect")
        inspect_option.click()
        context_menu.hide_popup_by_child_node(inspect_option)

        example_page.element_exists("inspect-menu-horizontal-splitter")
