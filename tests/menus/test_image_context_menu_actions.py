import platform
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_object import GenericPage
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2637622"

@pytest.fixture()
def delete_files_regex_string():
    return rf"{SAVED_FILENAME}"


LINK_IMAGE_URL = (
    "https://en.wikipedia.org/wiki/Firefox#/media/File:Firefox_logo,_2019.svg"
)
LOADED_IMAGE_URL = r"https://upload\.wikimedia\.org/wikipedia/commons/thumb/a/a0/Firefox_logo%2C_2019\.svg/\d+px-Firefox_logo%2C_2019\.svg\.png"
SAVED_FILENAME = "Firefox_logo,_2019.svg.png"


def test_open_image_in_new_tab(driver: Firefox):
    """
    C2637622.1: open an image in a new tab
    """
    # create objs
    wiki_image_page = GenericPage(driver, url=LINK_IMAGE_URL).open()
    image_context_menu = ContextMenu(driver)
    tabs = TabBar(driver)

    # wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # get the image and context click it
    image_logo = wiki_image_page.get_element("mediawiki-image")
    wiki_image_page.context_click(image_logo)

    # open in a new tab
    image_context_menu.click_and_hide_menu("context-menu-open-image-in-new-tab")

    # switch to the second tab and verify the URL
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])
    wiki_image_page.wait_for_page_to_load()
    wiki_image_page.verify_opened_image_url("wikimedia", LOADED_IMAGE_URL)


@pytest.mark.headed
def test_save_image_as(driver: Firefox, sys_platform, delete_files):
    """
    C2637622.2: save image as
    """
    try:
        from pynput.keyboard import Controller
    except ModuleNotFoundError:
        pytest.skip("Could not load pynput")

    controller = Controller()

    wiki_image_page = GenericPage(driver, url=LINK_IMAGE_URL).open()
    image_context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    util = Utilities()

    # Wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # Get the image and context click it
    image_logo = wiki_image_page.get_element("mediawiki-image")
    wiki_image_page.context_click(image_logo)

    # Save the image
    image_context_menu.click_and_hide_menu("context-menu-save-image-as")

    # wait some time before interacting with the system dialog
    sleep(2)
    wiki_image_page.handle_os_download_confirmation(controller, sys_platform)

    # Verify that the file exists
    sleep(2)
    saved_image_location = util.get_saved_file_path(SAVED_FILENAME)
    util.check_file_path_validility(saved_image_location)


def test_copy_image_link(driver: Firefox):
    """
    C2637622.3: copy an image link and verify its correct
    """
    # create objs
    nav = Navigation(driver)
    wiki_image_page = GenericPage(driver, url=LINK_IMAGE_URL).open()
    image_context_menu = ContextMenu(driver)
    tabs = TabBar(driver)

    # wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # get the image and context click it
    image_logo = wiki_image_page.get_element("mediawiki-image")
    wiki_image_page.context_click(image_logo)

    # copy the link
    image_context_menu.click_and_hide_menu("context-menu-copy-image-link")

    # open a new tab
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    # context click and paste
    search_bar = nav.get_awesome_bar()
    nav.context_click(search_bar)

    # paste and go
    nav.click_and_hide_menu("context-menu-paste-and-go")

    wiki_image_page.wait_for_page_to_load()
    with driver.context(driver.CONTEXT_CONTENT):
        wiki_image_page.verify_opened_image_url("wikimedia", LOADED_IMAGE_URL)
