import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

MP3_URL = "https://download.samplelib.com/mp3/sample-3s.mp3"
MP3_NAME_REGEX = r".*\.mp3(\s\(\d+\))?$"


@pytest.fixture()
def test_case():
    return "1836832"


@pytest.mark.headed
def test_download_mp3_and_check_extension(driver: Firefox):
    """
    1836829: Verify the mp3 filename shown in Firefox Downloads panel includes `.mp3`
    """
    nav = Navigation(driver)

    # Load a normal page
    page = GenericPage(driver, url="about:blank")
    page.open()

    # Simulate downloading the file by creating and clicking an anchor element
    driver.execute_script(
        """
        const a = document.createElement("a");
        a.href = arguments[0];
        a.click();
    """,
        MP3_URL,
    )

    # Dismiss "harmful file" warning if present
    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    # Wait for the download entry in the panel
    nav.element_visible("download-target-element")

    # Reuse the verification that already worked
    nav.verify_download_name(MP3_NAME_REGEX)
