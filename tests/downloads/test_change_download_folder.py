import os
import re
from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

FIRST_FILE_REGEX = r"sample-3s(\s\(\d+\))?\.mp3$"
SECOND_FILE_REGEX = r"sample-6s(\s\(\d+\))?\.mp3$"

# Downloads panel value (chrome) often contains full filename; allow duplicates.
MP3_PANEL_NAME_REGEX = r".*\.mp3(\s\(\d+\))?$"
MP3_DOWNLOAD_PAGE = "mp3_download.html"


@pytest.fixture()
def add_to_prefs_list():
    return [("media.play-stand-alone", False)]


@pytest.fixture()
def test_case():
    return "1756771"


@pytest.fixture()
def delete_files_regex_string():
    return r"sample-(3s|6s)(\s\(\d+\))?\.mp3$"


@pytest.fixture()
def temp_page(tmp_path):
    loc = tmp_path / MP3_DOWNLOAD_PAGE
    copyfile(f"data/pages/{MP3_DOWNLOAD_PAGE}", loc)
    return loc


@pytest.fixture()
def temp_selectors():
    return {
        "link-3s": {
            "selectorData": "mp3-link-3s",
            "strategy": "class",
            "groups": [],
        },
        "link-6s": {
            "selectorData": "mp3-link-6s",
            "strategy": "class",
            "groups": [],
        },
    }


def _set_download_dir(driver: Firefox, path: str) -> None:
    """Set the download directory via prefs (chrome context)."""
    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_script(
            """
            Services.prefs.setBoolPref("browser.download.useDownloadDir", true);
            Services.prefs.setIntPref("browser.download.folderList", 2);
            Services.prefs.setCharPref("browser.download.dir", arguments[0]);
            """,
            path,
        )


@pytest.mark.headed
def test_change_download_folder(
    driver: Firefox,
    downloads_folder: str,
    tmp_path,
    temp_page,
    temp_selectors,
    delete_files,
):
    """
    C1756713: Verify that the user can change the Download folder
    """

    nav = Navigation(driver)

    # Download a file (default folder)
    page = GenericPage(driver, url=f"file://{temp_page}")
    page.elements |= temp_selectors
    page.open()
    page.click_on("link-3s")

    nav.click_file_download_warning_panel()

    nav.element_visible("download-target-element")
    nav.wait_for_download_completion()
    nav.verify_download_name(MP3_PANEL_NAME_REGEX)

    first_pattern = re.compile(FIRST_FILE_REGEX)

    page.expect(
        lambda _: any(
            first_pattern.match(name) for name in os.listdir(downloads_folder)
        )
    )

    # Change the download folder (Save files to)
    custom_dir = tmp_path / "custom-downloads"
    custom_dir.mkdir(parents=True, exist_ok=True)
    _set_download_dir(driver, str(custom_dir))

    # Download another file (should land in new folder)
    page.click_on("link-6s")

    nav.click_file_download_warning_panel()

    nav.element_visible("download-target-element")
    nav.wait_for_download_completion()
    nav.verify_download_name(MP3_PANEL_NAME_REGEX)

    second_pattern = re.compile(SECOND_FILE_REGEX)

    page.expect(
        lambda _: any(second_pattern.match(name) for name in os.listdir(custom_dir))
    )
