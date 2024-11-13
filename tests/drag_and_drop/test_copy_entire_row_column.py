import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GoogleSheets, Navigation


@pytest.fixture()
def test_case():
    return "936861"


SHEET1_URL = "https://docs.google.com/spreadsheets/d/1kXW-a-ElKBykGTRO9vrwajYj_AHt9P-h8p3niLdXu40/edit?gid=0#gid=0"
SHEET2_URL = "https://docs.google.com/spreadsheets/d/1kXW-a-ElKBykGTRO9vrwajYj_AHt9P-h8p3niLdXu40/edit?gid=1387427752#gid=1387427752"


def test_copy_entire_row_column(driver: Firefox):
    """
    C936861: Verify that copying and pasting entire rows and columns work
    """
    # Initializing objects
    web_page = GoogleSheets(driver, url=SHEET1_URL).open()
    nav = Navigation(driver)

    try:
        # Copy a row
        web_page.select_num_rows(1)
        web_page.copy()

        # Paste the row in the same sheet
        for _ in range(3):
            web_page.perform_key_combo(Keys.ARROW_RIGHT, Keys.DOWN)
        web_page.paste()

        # Verify that the row is pasted properly
        for i in range(1, 4):
            web_page.element_attribute_contains(
                "formula-box-input", "innerHTML", str(i)
            )
            web_page.perform_key_combo(Keys.RIGHT)

        web_page.undo()

        # Paste the row in a different sheet
        nav.search(SHEET2_URL)
        time.sleep(2)
        web_page.paste()

        # Verify that the row is pasted properly
        for i in range(1, 4):
            web_page.element_attribute_contains(
                "formula-box-input", "innerHTML", str(i)
            )
            web_page.perform_key_combo(Keys.RIGHT)

        web_page.undo()

        # Copy a column
        nav.search(SHEET1_URL)
        time.sleep(2)
        web_page.select_num_columns(1)
        web_page.copy()

        # Paste the column in the same sheet
        for _ in range(3):
            web_page.perform_key_combo(Keys.ARROW_RIGHT, Keys.DOWN)
        web_page.paste()

        # Verify that the column is pasted properly
        for i in range(1, 4):
            web_page.element_attribute_contains(
                "formula-box-input", "innerHTML", str(i)
            )
            web_page.perform_key_combo(Keys.DOWN)

        web_page.undo()

        # Paste the column in a different sheet
        nav.search(SHEET2_URL)
        time.sleep(2)
        web_page.paste()

        # Verify that the column is pasted properly
        for i in range(1, 4):
            web_page.element_attribute_contains(
                "formula-box-input", "innerHTML", str(i)
            )
            web_page.perform_key_combo(Keys.DOWN)

    finally:
        web_page.undo()
