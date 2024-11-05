import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GoogleSheets


@pytest.fixture()
def test_case():
    return "936860"


SHEET_URL = "https://docs.google.com/spreadsheets/d/1ra7K1TAlns-X0mG93XWXC-P3lIEtLYuvXTGOVL8IqU8/edit?gid=0#gid=0"


def test_copy_table_header(driver: Firefox, sys_platform):
    """
    C936860: Verify that copying and pasting header from tables work
    """
    # Initializing objects
    web_page = GoogleSheets(driver, url=SHEET_URL).open()

    # Copy the header row
    web_page.select_num_rows(1)
    web_page.copy(sys_platform)

    # Paste the header row in the same sheet
    web_page.perform_key_combo(Keys.ARROW_RIGHT, Keys.DOWN, Keys.ARROW_RIGHT, Keys.DOWN, Keys.ARROW_RIGHT, Keys.DOWN)
    web_page.paste(sys_platform)

    # Verify that the pasted row has header attributes and the selection is pasted properly
    web_page.expect(lambda _: len(web_page.get_elements("table-options")) == 2)
    web_page.element_attribute_contains("text-colour", "style", "rgb(255, 255, 255)")
    web_page.element_attribute_contains("formula-box-input", "innerHTML", "Column 1") 
    web_page.perform_key_combo(Keys.ARROW_RIGHT)
    web_page.element_attribute_contains("formula-box-input", "innerHTML", "Column 2")
    web_page.undo(sys_platform)

    # Paste the header row in a different sheet
    web_page.cycle_to_next_sheet(sys_platform)
    web_page.paste(sys_platform)
        
    # Verify that the pasted row has header attributes and the selection is pasted properly
    web_page.expect(lambda _: len(web_page.get_elements("table-options")) == 1)
    web_page.element_attribute_contains("text-colour", "style", "rgb(255, 255, 255)")
    web_page.element_attribute_contains("formula-box-input", "innerHTML", "Column 1") 
    web_page.perform_key_combo(Keys.ARROW_RIGHT)
    web_page.element_attribute_contains("formula-box-input", "innerHTML", "Column 2")
    web_page.undo(sys_platform)
