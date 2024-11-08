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
DEFAULT_NAME = "Example Domain.pdf"


def file_is_somewhere():
    locs = [
        os.getcwd(),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
    ]
    for loc in locs:
        for _, _, files in os.walk(loc):
            if DEFAULT_NAME in files:
                logging.warning(f"File found in {loc}")
                return True
    return False


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

    print_preview.expect(lambda _: file_is_somewhere())
