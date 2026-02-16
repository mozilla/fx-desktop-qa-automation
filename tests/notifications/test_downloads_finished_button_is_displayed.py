import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

TEST_URL = "https://download.samplelib.com/mp3/sample-3s.mp3"


@pytest.fixture()
def test_case():
    return "125307"


@pytest.fixture()
def delete_files_regex_string():
    return r"sample-3s(\s\(\d+\))?\.mp3$"


def _trigger_download(driver: Firefox, url: str) -> None:
    """Create + click an anchor."""
    driver.execute_script(
        """
        const a = document.createElement("a");
        a.href = arguments[0];
        a.click();
        """,
        url,
    )


@pytest.mark.headed
def test_download_complete_icon_is_displayed(driver: Firefox, delete_files):
    """
    C125307 - Download a valid file and wait for the download to complete.
    Verify the completed download icon/state is displayed.
    """
    nav = Navigation(driver)
    page = GenericPage(driver, url="about:blank")
    page.open()

    # Trigger download
    _trigger_download(driver, TEST_URL)

    # Optional warning panel in some environments
    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    # Wait for download to start + complete (existing downloads pattern)
    nav.element_visible("download-target-element")
    nav.wait_for_download_completion()

    # Completed state: "finish" indicator box is displayed in chrome UI
    nav.expect_in_chrome(
        lambda _: nav.get_element("downloads-indicator-finish-box").is_displayed()
    )
