from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "1756752"


@pytest.fixture()
def delete_files_regex_string():
    return r"pdf-example-bookmarks.pdf"


CONTENT_DISPOSITION_ATTACHMENT_URL = (
    "https://download.novapdf.com/download/samples/pdf-example-bookmarks.pdf"
)


@pytest.mark.ci
def test_set_always_ask_file_type(driver: Firefox, delete_files):
    """
    C1756752 - Ensure that the Always ask option in Firefox Applications settings
    leads to a dialog asking "What should Firefox do with this file?" when the file type
    is downloaded.
    """

    # Initialize page objects
    nav = Navigation(driver)
    about_prefs = AboutPrefs(driver, category="general")

    # Set PDF handling to "Always ask"
    about_prefs.open()
    about_prefs.set_pdf_handling_to_always_ask()

    # Navigate to download URL and verify dialog appears
    nav.search(CONTENT_DISPOSITION_ATTACHMENT_URL)

    # Wait for and handle the unknown content type dialog
    about_prefs.handle_unknown_content_dialog()
