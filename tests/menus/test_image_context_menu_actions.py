import os
import re
from time import monotonic, sleep

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
    # Clear every saved variant (any extension/suffix); a leftover triggers a
    # "replace?" prompt that cancels the save.
    return rf"{re.escape(SAVED_IMAGE_STEM)}.*"


LINK_IMAGE_URL = (
    "https://en.wikipedia.org/wiki/Firefox#/media/File:Firefox_logo,_2019.svg"
)
LOADED_IMAGE_URL = (
    r"https://upload\.wikimedia\.org/wikipedia/commons/thumb/a/a0/Firefox_logo%2C_2019\.svg/\d+px"
    r"-Firefox_logo%2C_2019\.svg\.png"
)
# Match the saved file by stem; the served format varies (.webp/.png).
SAVED_IMAGE_STEM = "Firefox_logo,_2019.svg"
# Poll for the saved file, re-confirming the save dialog each tick.
SAVE_TIMEOUT_SECONDS = 15
SAVE_POLL_INTERVAL_SECONDS = 1


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
    wiki_image_page = GenericPage(driver, url=LINK_IMAGE_URL)
    wiki_image_page.open()
    image_context_menu = ContextMenu(driver)
    util = Utilities()

    # Wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # Get the image and context click it
    image_logo = wiki_image_page.get_element("mediawiki-image")
    wiki_image_page.context_click(image_logo)

    # Save the image
    image_context_menu.click_and_hide_menu("context-menu-save-image-as")

    # The save dialog opens after a variable delay, so re-confirm on a poll loop
    # until a non-empty file matching the stem appears.
    downloads_dir = os.path.dirname(util.get_saved_file_path(SAVED_IMAGE_STEM))
    saved_image_location = None
    end_time = monotonic() + SAVE_TIMEOUT_SECONDS
    while monotonic() < end_time:
        wiki_image_page.handle_os_download_confirmation()
        saved_image_location = next(
            (
                os.path.join(downloads_dir, name)
                for name in os.listdir(downloads_dir)
                if name.startswith(SAVED_IMAGE_STEM)
                and os.path.getsize(os.path.join(downloads_dir, name)) > 0
            ),
            None,
        )
        if saved_image_location:
            break
        sleep(SAVE_POLL_INTERVAL_SECONDS)

    assert saved_image_location, (
        f"No saved image matching '{SAVED_IMAGE_STEM}*' found in {downloads_dir}"
    )


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
    wiki_image_page.verify_opened_image_url("wikimedia", LOADED_IMAGE_URL)
