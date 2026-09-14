import re
from pathlib import Path

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
# The thumbnail host varies (upload/thumb) and may have a query string.
LOADED_IMAGE_URL = (
    r"https://[a-zA-Z0-9-]+\.wikimedia\.org/wikipedia/commons/thumb/a/a0/Firefox_logo%2C_2019\.svg/\d+px"
    r"-Firefox_logo%2C_2019\.svg\.png"
)
# Match the saved file by stem; the served format varies (.webp/.png).
SAVED_IMAGE_STEM = "Firefox_logo,_2019.svg"
# Mock picker needs a deterministic target path; the extension is the test's
# choice (we only verify a non-empty file was saved).
SAVED_IMAGE_FILENAME = f"{SAVED_IMAGE_STEM}.png"
SAVE_TIMEOUT_SECONDS = 15


def new_tab_handle(driver: Firefox, original_handles: set[str]) -> str:
    """Return the handle of the tab opened since original_handles was taken."""
    new_handles = set(driver.window_handles) - original_handles
    assert len(new_handles) == 1, f"Expected exactly one new tab, got {new_handles}"
    return new_handles.pop()


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

    # note the open tabs so we can pick out the new one
    original_handles = set(driver.window_handles)

    # open in a new tab
    image_context_menu.click_and_hide_menu("context-menu-open-image-in-new-tab")

    # switch to the new tab and verify the URL
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(new_tab_handle(driver, original_handles))
    wiki_image_page.wait_for_page_to_load()
    wiki_image_page.verify_opened_image_url("wikimedia", LOADED_IMAGE_URL)


def test_save_image_as(driver: Firefox, downloads_folder, delete_files):
    """
    C2637622.2: save image as
    """
    wiki_image_page = GenericPage(driver, url=LINK_IMAGE_URL).open()
    image_context_menu = ContextMenu(driver)

    # Wait for page to load
    wiki_image_page.wait_for_page_to_load()

    # Get the image and context click it
    image_logo = wiki_image_page.get_element("mediawiki-image")
    wiki_image_page.context_click(image_logo)

    # mock the native save dialog, which CI cannot drive reliably
    saved_image_location = Path(downloads_folder) / SAVED_IMAGE_FILENAME
    wiki_image_page.install_mock_file_picker(str(saved_image_location))
    try:
        # Save the image
        image_context_menu.click_and_hide_menu("context-menu-save-image-as")
        wiki_image_page.wait_for_mock_file_picker()
    finally:
        wiki_image_page.cleanup_mock_file_picker()

    # verify a non-empty file was written
    wiki_image_page.custom_wait(timeout=SAVE_TIMEOUT_SECONDS).until(
        lambda _: saved_image_location.exists()
        and saved_image_location.stat().st_size > 0,
        message=f"No non-empty saved image at {saved_image_location}",
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

    # open a new tab and switch to it
    original_handles = set(driver.window_handles)
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(new_tab_handle(driver, original_handles))

    # context click and paste
    search_bar = nav.get_awesome_bar()
    nav.context_click(search_bar)

    # paste and go
    nav.click_and_hide_menu("context-menu-paste-and-go")

    wiki_image_page.wait_for_page_to_load()
    wiki_image_page.verify_opened_image_url("wikimedia", LOADED_IMAGE_URL)
