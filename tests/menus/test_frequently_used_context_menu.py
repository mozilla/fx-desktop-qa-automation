import os
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Devtools, Navigation
from modules.page_object import ExamplePage
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2637623"


# Test is unstable for now
@pytest.mark.headed
def test_save_page_as(driver: Firefox, sys_platform):
    """
    C2637623.1: save page as
    """
    try:
        from pynput.keyboard import Controller
    except ModuleNotFoundError:
        pytest.skip("Could not load pynput")

    controller = Controller()

    # create objects
    context_menu = ContextMenu(driver)
    driver.get("https://example.com")
    example_page = ExamplePage(driver)
    nav = Navigation(driver)
    util = Utilities()

    # right click something that is not a hyperlink
    title_header = example_page.get_element("title-header")
    example_page.context_click(title_header)

    context_menu.click_and_hide_menu("context-menu-save-page-as")

    # short sleep to ensure menu is shown
    sleep(2)
    context_menu.handle_os_download_confirmation(controller, sys_platform)

    # Wait for the animation to complete
    nav.wait_for_download_animation_finish()

    # verify and delete downloaded file
    saved_image_location = util.get_saved_file_path("Example Domain.html")
    example_page.expect(lambda _: os.path.exists(saved_image_location))
    util.remove_file(saved_image_location)


def test_take_screenshot(driver: Firefox):
    """
    C2637623.2: take screenshot works from context menu
    """
    # create objects
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    driver.get("https://example.com")
    example_page = ExamplePage(driver)
    example_page.open()

    # ensure that the screenshot is not present
    example_page.element_does_not_exist("take-screenshot-box")
    example_page.context_click("title-header")

    # context click the screenshot option and verify its not hidden
    context_menu.click_and_hide_menu("context-menu-take-screenshot")
    nav.element_exists("content-area-menu")


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
    example_page.get_element("title-header")
    example_page.context_click("title-header")

    context_menu.click_and_hide_menu("context-menu-inspect")

    devtools.check_opened()
