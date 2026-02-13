import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

TEST_URL = "https://download.samplelib.com/mp3/sample-3s.mp3"


@pytest.fixture()
def test_case():
    return "125308"


def _trigger_download(driver: Firefox, url: str) -> None:
    driver.execute_script(
        """
        const a = document.createElement("a");
        a.href = arguments[0];
        a.click();
        """,
        url,
    )


@pytest.mark.headed
def test_downloads_icon_is_displayed_after_download(driver: Firefox):
    """
    C125308 - Verify that the Downloads toolbar icon is displayed after a download starts.
    """
    nav = Navigation(driver)
    page = GenericPage(driver, url="about:blank")
    page.open()

    # Trigger download
    _trigger_download(driver, TEST_URL)

    try:
        nav.click_file_download_warning_panel()
    except Exception:
        pass

    # Wait for download to start
    nav.element_visible("download-target-element")

    # Assert Downloads toolbar button is visible (chrome context)
    nav.expect_in_chrome(lambda _: nav.get_element("downloads-button").is_displayed())
