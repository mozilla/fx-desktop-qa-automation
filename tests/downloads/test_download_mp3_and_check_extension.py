from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

MP3_NAME_REGEX = r".*\.mp3(\s\(\d+\))?$"
MP3_DOWNLOAD_PAGE = "mp3_download.html"


@pytest.fixture()
def delete_files_regex_string():
    return r"sample-(3s)(\s\(\d+\))?\.mp3$"


@pytest.fixture()
def test_case():
    return "1836832"


@pytest.fixture()
def add_to_prefs_list():
    return [("media.play-stand-alone", False)]


@pytest.fixture()
def temp_page(tmp_path):
    loc = tmp_path / MP3_DOWNLOAD_PAGE
    copyfile(f"data/pages/{MP3_DOWNLOAD_PAGE}", loc)
    return loc


@pytest.fixture()
def temp_selectors():
    return {
        "download-link": {
            "selectorData": "mp3-link-3s",
            "strategy": "class",
            "groups": [],
        }
    }


@pytest.mark.headed
def test_download_mp3_and_check_extension(
    driver: Firefox, temp_page, temp_selectors, delete_files
):
    """
    1836829: Verify the mp3 filename shown in Firefox Downloads panel includes `.mp3`
    """
    nav = Navigation(driver)

    # Load test page

    url = f"file://{temp_page}"
    page = GenericPage(driver, url=url)
    page.elements |= temp_selectors
    page.open()

    page.click_on("download-link")

    # Dismiss "harmful file" warning if present
    nav.click_file_download_warning_panel()

    # Wait for the download entry in the panel
    nav.element_visible("download-target-element")

    # Reuse the verification that already worked
    nav.verify_download_name(MP3_NAME_REGEX)
