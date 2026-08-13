import os
import re
from time import monotonic, sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "2637622"


@pytest.fixture()
def delete_files_regex_string():
    # Clear every saved variant (any extension/suffix) so no leftover interferes
    # with the save.
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
# Mock picker needs a deterministic target path; the extension is the test's
# choice (we only verify a non-empty file was saved). Native saves are auto-named.
SAVED_IMAGE_FILENAME = f"{SAVED_IMAGE_STEM}.png"
# Poll for the saved file, re-confirming the native save dialog each tick.
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
def test_save_image_as(driver: Firefox, sys_platform, downloads_folder, delete_files):
    """
    C2637622.2: save image as
    """
    wiki_image_page = GenericPage(driver, url=LINK_IMAGE_URL)
    wiki_image_page.open()
    image_context_menu = ContextMenu(driver)

    # Wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # Get the image and context click it
    image_logo = wiki_image_page.get_element("mediawiki-image")
    wiki_image_page.context_click(image_logo)

    # Linux CI can't reliably drive the native "Save As" dialog, so use the mock
    # file picker, which is the repo convention for downloads. Other platforms
    # confirm the native dialog.
    use_mock_picker = sys_platform == "Linux"
    mock_saved_image_location = os.path.join(downloads_folder, SAVED_IMAGE_FILENAME)
    if use_mock_picker:
        wiki_image_page.install_mock_file_picker(mock_saved_image_location)

    try:
        # Save the image
        image_context_menu.click_and_hide_menu("context-menu-save-image-as")

        if use_mock_picker:
            wiki_image_page.wait_for_mock_file_picker()
            wiki_image_page.custom_wait(timeout=SAVE_TIMEOUT_SECONDS).until(
                lambda _: (
                    os.path.exists(mock_saved_image_location)
                    and os.path.getsize(mock_saved_image_location) > 0
                ),
                message=f"No non-empty saved image at {mock_saved_image_location}",
            )
        else:
            # Native dialog path: the save dialog opens after a variable delay, so
            # re-confirm on a poll loop until a non-empty file matching the stem appears.
            saved_image_location = None
            end_time = monotonic() + SAVE_TIMEOUT_SECONDS
            while monotonic() < end_time:
                wiki_image_page.handle_os_download_confirmation()
                saved_image_location = next(
                    (
                        os.path.join(downloads_folder, name)
                        for name in os.listdir(downloads_folder)
                        if name.startswith(SAVED_IMAGE_STEM)
                        and os.path.getsize(os.path.join(downloads_folder, name)) > 0
                    ),
                    None,
                )
                if saved_image_location:
                    break
                sleep(SAVE_POLL_INTERVAL_SECONDS)

            assert saved_image_location, (
                f"No saved image matching '{SAVED_IMAGE_STEM}*' found in {downloads_folder}"
            )
    finally:
        if use_mock_picker:
            wiki_image_page.cleanup_mock_file_picker()


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
