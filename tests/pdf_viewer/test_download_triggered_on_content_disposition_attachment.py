from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs, GenericPdf
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "936502"


@pytest.fixture()
def delete_files_regex_string():
    return r"pdf-example-bookmarks.pdf"


CONTENT_DISPOSITION_ATTACHMENT_URL = (
    "https://download.novapdf.com/download/samples/pdf-example-bookmarks.pdf"
)


def test_download_panel_triggered_on_content_disposition_attachment(
    driver: Firefox, delete_files
):
    """
    C936502: Ensure that the Always ask option in Firefox Applications settings
    triggers the download panel for PDFs with Content-Disposition: attachment.

    Arguments:
        delete_files: fixture to remove the files after the test finishes
    """

    # Instantiate object models
    tabs = TabBar(driver)
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general").open()
    browser_actions = BrowserActions(driver)
    # search for Applications section in settings
    about_prefs.find_in_settings("appl")
    # set download option for pdf as always ask
    about_prefs.select_content_and_action("application/pdf", "Always ask")
    # search pdf file
    nav.search(CONTENT_DISPOSITION_ATTACHMENT_URL)
    # wait till open option is available
    sleep(3)

    browser_actions.select_file_opening_option()

    tabs.wait_for_num_tabs(2)
    assert (
        len(driver.window_handles) == 2
    ), f"Expected 2 tabs, but found {len(driver.window_handles)}"

    tabs.switch_to_new_tab()
    GenericPdf(driver, pdf_url="").url_contains("file:")
