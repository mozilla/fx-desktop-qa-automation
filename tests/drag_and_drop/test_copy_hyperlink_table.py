from time import sleep

import pytest
from selenium.webdriver import Firefox, Keys

from modules.page_object import GoogleSheets, Navigation


@pytest.fixture()
def test_case():
    return "937418"


@pytest.fixture()
def temp_selectors():
    return {
        "cell-link": {
            "selectorData": "docs-linkbubble-link-text",
            "strategy": "id",
            "groups": [],
        }
    }


SHEET1_URL = "https://docs.google.com/spreadsheets/d/1ennETYnxeWZrUcItUxHgR8ug6EwL_QpyUFvB4I7lof4/edit?usp=sharing"
SHEET2_URL = (
    "https://docs.google.com/spreadsheets/d/1ennETYnxeWZrUcItUxHgR8ug6EwL_QpyUFvB4I7lof4/edit?gid=674466887"
    "#gid=674466887"
)

expected_values = [
    ["Season", "Ordered", "First aired"],
    ["Season 1", "3/2/2010", "4/17/2011"],
]


@pytest.mark.headed
def test_copy_table_with_hyperlink(driver: Firefox, temp_selectors):
    """
    Verify that copying and pasting table content with hyperlinks retains the hyperlink functionality and redirects
    to the correct page.
    """
    # Initializing objects
    web_page = GoogleSheets(driver, url=SHEET1_URL).open()
    nav = Navigation(driver)
    web_page.elements |= temp_selectors

    try:
        # Copy the table
        web_page.select_num_rows(2)
        web_page.copy()

        nav.search(SHEET2_URL)
        sleep(2)
        web_page.paste()

        # Move to the starting cell (A1)
        web_page.perform_key_combo(Keys.HOME)

        # Verify that the pasted values are correct
        for row_index, row in enumerate(expected_values):
            for col_index, expected_value in enumerate(row):
                web_page.element_attribute_contains(
                    "formula-box-input", "innerHTML", expected_value
                )
                # Move to the next cell to the right
                web_page.perform_key_combo(Keys.RIGHT)
            # Move to the beginning of the next row
            web_page.perform_key_combo(Keys.HOME)
            # Move down to the next row
            web_page.perform_key_combo(Keys.DOWN)

        # Move to the cell containing the hyperlink
        web_page.perform_key_combo(Keys.HOME)
        web_page.perform_key_combo(Keys.UP)

        # Click on the hyperlink
        web_page.perform_key_combo(Keys.ENTER)
        web_page.element_clickable("cell-link")
        web_page.click_on("cell-link")

        # Verify that the user is redirected to the correct page
        driver.switch_to.window(driver.window_handles[-1])
        web_page.url_contains("Game_of_Thrones_season_1")

        # Close the new tab and switch the focus to prevent the "Leave Page" warning from Google page
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        sleep(1)

        # Delete the pasted table
        web_page.perform_key_combo(Keys.ESCAPE)
        web_page.perform_key_combo(Keys.ESCAPE)
        web_page.select_entire_table()
        web_page.perform_key_combo(Keys.BACK_SPACE)

    except Exception:
        web_page.undo()

    finally:
        sleep(2)
