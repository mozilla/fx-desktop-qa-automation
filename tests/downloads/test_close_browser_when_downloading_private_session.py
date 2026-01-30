import pytest
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage

TEST_URL = "https://ash-speed.hetzner.com/"


@pytest.fixture()
def test_case():
    return "1756696"

@pytest.mark.headed
def test_close_browser_with_download_in_progress_shows_prompt(driver):
    """
    C1756696 - Close Firefox while a download is in progress in Private Browsing
    and verify the 'Cancel All Downloads?' prompt is shown.
    """

    nav = Navigation(driver)
    page = GenericPage(driver, url=TEST_URL)

    nav.open_and_switch_to_new_window("private")

    page.open()
    page.click_on("sample-bin-download")

    nav.attempt_close_window()

    def prompt_visible(_):
        dialog = nav.get_element("common-dialog-window")
        return dialog.is_displayed() and "Cancel All Downloads?" in dialog.text

    WebDriverWait(driver, 10).until(prompt_visible)