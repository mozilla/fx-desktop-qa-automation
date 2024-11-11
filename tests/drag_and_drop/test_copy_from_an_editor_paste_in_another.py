from time import sleep

import pytest
from selenium.webdriver import Firefox, Keys

from modules.page_object_google import GoogleSheets


@pytest.fixture()
def test_case():
    return "936864"


SHEET1_URL = "https://docs.google.com/spreadsheets/d/1HDwm0E77eyVkMQYiDkCCBp3lep4n9Mq0pW7uVE6yncg/edit?usp=sharing"
SHEET2_URL = "https://online.visual-paradigm.com/app/office/#proj=0&type=Spreadsheet&office-new"


def test_copy_from_an_editor_paste_in_another(driver: Firefox, sys_platform):
    """
    C936864: Pressing “Ctrl” key to select and copy multiple rows/columns of a table from an online editor then pasting
    to another online editor
    """
    # Initializing objects
    web_page = GoogleSheets(driver, url=SHEET1_URL).open()

    # Copy the header row
    web_page.select_num_rows(5)
    web_page.copy(sys_platform)

    GoogleSheets(driver, url=SHEET2_URL).open()
    web_page.paste(sys_platform)
    sleep(1000)
