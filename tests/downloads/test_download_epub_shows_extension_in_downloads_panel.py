import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

EPUB_URL = "https://www.gutenberg.org/ebooks/68473.epub.noimages?session_id=f8278dd40b5d1ac1078d21601c5f150d9b35b4ad"
EPUB_NAME_REGEX = r".*\.epub(\s\(\d+\))?$"


@pytest.fixture()
def test_case():
    return "1836831"


@pytest.mark.headed
def test_download_epub_and_check_extension(driver: Firefox):
    """
    1836831: Verify the EPUB filename shown in Firefox Downloads panel includes `.epub`
    """
    nav = Navigation(driver)

    # Load a normal page
    page = GenericPage(driver, url="about:blank")
    page.open()

    # Simulate downloading the file by creating and clicking an anchor element
    driver.execute_script(
        """
        const url = arguments[0];
        const a = document.createElement("a");
        a.href = url;
        a.target = "_self";
        a.rel = "noopener noreferrer";
        document.body.appendChild(a);
        a.click();
        a.remove();
        """,
        EPUB_URL,
    )

    # If Firefox shows a warning panel, dismiss it (safe call: waits/clicks only if present)
    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    # Wait for the download entry in the panel UI
    nav.element_visible("download-target-element")

    # Assert the filename ends with .epub (allow "(1)" etc.)
    nav.verify_download_name(EPUB_NAME_REGEX)
