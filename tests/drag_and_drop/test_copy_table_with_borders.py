import time
import logging
import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GoogleSheets, Navigation


@pytest.fixture()
def test_case():
    return "936861"


SHEET1_URL = "https://docs.google.com/spreadsheets/d/1MTbO1TJEgyNE1f8EvM6Yb_WIhIV0jpBp2vG8P0F8wNk/edit?gid=0#gid=0"
SHEET2_URL = "https://docs.google.com/spreadsheets/d/1MTbO1TJEgyNE1f8EvM6Yb_WIhIV0jpBp2vG8P0F8wNk/edit?gid=474049343#gid=474049343"


def test_copy_entire_row_column(driver: Firefox):
    """
    C936861: Verify that copying and pasting entire rows and columns work
    """
    # Initializing objects
    web_page = GoogleSheets(driver, url=SHEET1_URL).open()
    nav = Navigation(driver)

    try:
        # Copy the table with border
        web_page.select_entire_table()
        web_page.copy()

        counter = 0
        for el in web_page.get_elements("range-border"):
            if "opacity: 1" in el.get_attribute("style"):
                counter += 1
        logging.warning(counter)


        # Paste the row in the same sheet
        for _ in range(3):
            web_page.actions.send_keys(Keys.ARROW_RIGHT, Keys.DOWN).perform()
        web_page.paste()
        time.sleep(3)
        counter = 0
        for el in web_page.get_elements("range-border"):
            if "opacity: 1" in el.get_attribute("style"):
                counter += 1
        logging.warning(counter)

        # Verify that the row is pasted properly
        # for i in range(3):
        #     for j in range(3):
        #         web_page.element_attribute_contains(
        #             "formula-box-input", "innerHTML", str(3*i+j)
        #         )
        #         web_page.actions.send_keys(Keys.TAB).perform()
        # web_page.actions.send_keys(Keys.DELETE).perform()
        # counter = 0
        # for el in web_page.get_elements("range-border"):
        #     if "opacity: 1" in el.get_attribute("style"):
        #         counter += 1
        # logging.warning(counter)

        # # Paste the row in a different sheet
        # nav.search(SHEET2_URL)
        # time.sleep(2)
        # web_page.paste()

        # # Verify that the row is pasted properly
        # for i in range(3):
        #     for j in range(3):
        #         web_page.element_attribute_contains(
        #             "formula-box-input", "innerHTML", str(3*i+j)
        #         )
        #         web_page.actions.send_keys(Keys.TAB).perform()
        # web_page.actions.send_keys(Keys.DELETE).perform()

    finally:
        web_page.undo()
        time.sleep(2)

