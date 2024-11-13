import platform
import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.page_object import GoogleSheets, Navigation


@pytest.fixture()
def test_case():
    return "936860"


SHEET_SETS = {
    "Darwin": (
        "https://docs.google.com/spreadsheets/d/1ra7K1TAlns-X0mG93XWXC-P3lIEtLYuvXTGOVL8IqU8/edit?gid=1469667334#gid=1469667334",
        "https://docs.google.com/spreadsheets/d/1ra7K1TAlns-X0mG93XWXC-P3lIEtLYuvXTGOVL8IqU8/edit?gid=1776043530#gid=1776043530",
    ),
    "Windows": (
        "https://docs.google.com/spreadsheets/d/1cxDppB_yNeMoUSaOqK-Hq6OS08kbOSeLck6Kypyb4zg/edit?gid=1469667334#gid=1469667334",
        "https://docs.google.com/spreadsheets/d/1cxDppB_yNeMoUSaOqK-Hq6OS08kbOSeLck6Kypyb4zg/edit?gid=1776043530#gid=1776043530",
    ),
    "Linux": (
        "https://docs.google.com/spreadsheets/d/1CuxT_RgsLonZSGXXhCgc4648mGtXUW1iii0qPwMxn3Q/edit?gid=1469667334#gid=1469667334",
        "https://docs.google.com/spreadsheets/d/1CuxT_RgsLonZSGXXhCgc4648mGtXUW1iii0qPwMxn3Q/edit?gid=1776043530#gid=1776043530",
    ),
}


@pytest.mark.headed
@pytest.mark.xfail(platform.system == "Linux", reason="Unstable in TC linux")
def test_copy_table_header(driver: Firefox):
    """
    C936860: Verify that copying and pasting header from tables work
    """
    (sheet1_url, sheet2_url) = SHEET_SETS.get(platform.system())
    # Initializing objects
    web_page = GoogleSheets(driver, url=sheet1_url).open()
    nav = Navigation(driver)

    # Copy the header row
    web_page.select_num_rows(1)
    web_page.copy(platform.system())

    try:
        # Paste the header row in the same sheet
        for _ in range(3):
            web_page.perform_key_combo(Keys.ARROW_RIGHT, Keys.DOWN)
        web_page.paste(platform.system())

        # Verify that the pasted row has header attributes and the selection is pasted properly
        web_page.expect(lambda _: len(web_page.get_elements("table-options")) == 2)
        web_page.element_attribute_contains(
            "text-colour", "style", "rgb(255, 255, 255)"
        )
        web_page.element_attribute_contains(
            "formula-box-input", "innerHTML", "Column 1"
        )
        web_page.perform_key_combo(Keys.ARROW_RIGHT)
        web_page.element_attribute_contains(
            "formula-box-input", "innerHTML", "Column 2"
        )
        web_page.undo(platform.system())

        # Paste the header row in a different sheet
        nav.search(sheet2_url)
        time.sleep(2)
        web_page.paste(platform.system())

        # Verify that the pasted row has header attributes and the selection is pasted properly
        web_page.expect(lambda _: len(web_page.get_elements("table-options")) == 1)
        web_page.element_attribute_contains(
            "text-colour", "style", "rgb(255, 255, 255)"
        )
        web_page.element_attribute_contains(
            "formula-box-input", "innerHTML", "Column 1"
        )
        web_page.perform_key_combo(Keys.ARROW_RIGHT)
        web_page.element_attribute_contains(
            "formula-box-input", "innerHTML", "Column 2"
        )
        web_page.undo(platform.system())
    finally:
        web_page.undo(platform.system())
    time.sleep(2)
