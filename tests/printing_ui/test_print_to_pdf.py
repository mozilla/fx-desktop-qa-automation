import logging
import os
from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import PrintPreview
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "965142"


@pytest.fixture()
def delete_files_regex_string():
    return r".*Example Domain.pdf"


@pytest.fixture()
def set_prefs():
    return [
        ("print_printer", "Mozilla Save to PDF"),
        ("print.save_print_settings", False),
        ("print.print_to_file", True),
    ]


TEST_PAGE = "https://example.com"


@pytest.mark.headed
def test_print_to_pdf(
    driver: Firefox,
    downloads_folder: str,
    sys_platform,
    delete_files,
):
    """
    C965142 - Verify that the user can print a webpage to PDF
    """

    driver.get(TEST_PAGE)

    # Select Print option from Hamburger Menu in order to trigger the silent printing
    print_preview = PrintPreview(driver)
    print_preview.open()
    print_preview.start_print()

    docs_location = os.path.join(
        os.path.dirname(downloads_folder), "Documents", "Example Domain.pdf"
    )
    if sys_platform == "Linux":
        docs_location = os.path.join(downloads_folder, "Example Domain.pdf")
    sleep(6)
    logging.warning(str(os.listdir(os.path.dirname(docs_location))))
    print_preview.expect(lambda _: os.path.exists())
