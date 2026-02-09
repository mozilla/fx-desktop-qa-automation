import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

TEST_URL = "https://ash-speed.hetzner.com/"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def test_case():
    return "1756765"


def test_delete_download_while_in_progress(driver: Firefox):
    """
    C1756765 - Verify that the user can Delete downloads while download is in progress
    """

    # Instantiate object
    page = GenericPage(driver, url=TEST_URL)
    nav = Navigation(driver)

    # Open test url and download a file
    page.open()
    page.click_on("sample-bin-download")

    # While download is in progress, right-click on the download item from the Downloads Panel and select delete
    nav.perform_download_context_action("context-menu-delete")

    # Verify that the "File deleted" message is displayed
    nav.element_visible("download-deleted-message")
