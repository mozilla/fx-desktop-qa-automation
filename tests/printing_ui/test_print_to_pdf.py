import os
from time import sleep

import pytest
from pynput.keyboard import Controller, Key
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, PrintPreview


@pytest.fixture()
def test_case():
    return "965142"


@pytest.fixture()
def delete_files_regex_string():
    return r".*wikipedia.pdf"


# @pytest.fixture()
# def set_prefs():
#    return [("print.always_print_silent", True)]


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

    # keyboard = Controller()
    # panel_ui = PanelUi(driver)

    driver.get(TEST_PAGE)

    # Select Print option from Hamburger Menu in order to trigger the silent printing
    print_preview = PrintPreview(driver)
    print_preview.open()
    print_preview.select_print_to_pdf()
    sleep(10)
