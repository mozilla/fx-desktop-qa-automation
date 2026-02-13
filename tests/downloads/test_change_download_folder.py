import os
import re

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

FIRST_FILE_URL = "https://download.samplelib.com/mp3/sample-3s.mp3"
SECOND_FILE_URL = "https://download.samplelib.com/mp3/sample-6s.mp3"

FIRST_FILE_REGEX = r"sample-3s(\s\(\d+\))?\.mp3$"
SECOND_FILE_REGEX = r"sample-6s(\s\(\d+\))?\.mp3$"

# Downloads panel value (chrome) often contains full filename; allow duplicates.
MP3_PANEL_NAME_REGEX = r".*\.mp3(\s\(\d+\))?$"


@pytest.fixture()
def test_case():
    return "1756771"


@pytest.fixture()
def delete_files_regex_string():
    return r"sample-(3s|6s)(\s\(\d+\))?\.mp3$"


def _trigger_download(driver: Firefox, url: str) -> None:
    """Reuse the downloads test pattern: create + click an anchor."""
    driver.execute_script(
        """
        const a = document.createElement("a");
        a.href = arguments[0];
        a.click();
        """,
        url,
    )



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
    delete_files,
):
    """
    C1756713: Verify that the user can change the Download folder
    """

    nav = Navigation(driver)

    # Download a file (default folder)
    page = GenericPage(driver, url="about:blank")
    page.open()
    _trigger_download(driver, FIRST_FILE_URL)

    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    nav.element_visible("download-target-element")
    nav.wait_for_download_completion()
    nav.verify_download_name(MP3_PANEL_NAME_REGEX)

    first_pattern = re.compile(FIRST_FILE_REGEX)

    page.expect(
        lambda _: any(
            first_pattern.match(name)
            for name in os.listdir(downloads_folder)
        )
    )

    # Go to about:preferences and search for "Downloads"
    prefs = AboutPrefs(driver, category="general")
    prefs.open()
    prefs.find_in_settings("Downloads")

    # Change the download folder (Save files to)
    custom_dir = tmp_path / "custom-downloads"
    custom_dir.mkdir(parents=True, exist_ok=True)
    _set_download_dir(driver, str(custom_dir))

    # Download another file (should land in new folder)
    page.open()
    _trigger_download(driver, SECOND_FILE_URL)

    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    nav.element_visible("download-target-element")
    nav.wait_for_download_completion()
    nav.verify_download_name(MP3_PANEL_NAME_REGEX)

    second_pattern = re.compile(SECOND_FILE_REGEX)

    page.expect(
        lambda _: any(
            second_pattern.match(name)
            for name in os.listdir(custom_dir)
        )
    )