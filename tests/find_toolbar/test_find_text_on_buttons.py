import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import FindToolbar
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "127250"


# Color-count difference that means the highlight changed
TOLERANCE = 3

TARGET_PAGE = "about:support"
SEARCH_TERM = "clipboard"

# Two buttons on about:support contain the search term
first_button = (By.CSS_SELECTOR, "#copy-raw-data-to-clipboard")
second_button = (By.CSS_SELECTOR, "#copy-to-clipboard")


def are_lists_different(a: int, b: int) -> bool:
    return abs(a - b) > TOLERANCE


def test_find_text_on_buttons(
    driver: Firefox, find_toolbar: FindToolbar, browser_actions: BrowserActions
):
    """
    C127250: Verify that searching for text that appears on buttons works properly

    Arguments:
        browser_actions: instantiation of BrowserActions BOM.
        find_toolbar: instantiation of FindToolbar BOM.
    """
    driver.get(TARGET_PAGE)

    # Reference colors for both buttons before anything is highlighted
    first_ref_colors = browser_actions.get_all_colors_in_element(first_button)
    second_ref_colors = browser_actions.get_all_colors_in_element(second_button)

    # Every instance of the term on the buttons is found
    find_toolbar.open()
    find_toolbar.find(SEARCH_TERM)
    assert find_toolbar.match_dict["total"] == 2

    # Only the first match is highlighted
    find_toolbar.rewind_to_first_match()
    first_colors = browser_actions.get_all_colors_in_element(first_button)
    second_colors = browser_actions.get_all_colors_in_element(second_button)

    assert are_lists_different(len(first_colors), len(first_ref_colors))
    assert not are_lists_different(len(second_colors), len(second_ref_colors))

    # Going forward moves the highlight to the second match
    find_toolbar.next_match()
    first_colors = browser_actions.get_all_colors_in_element(first_button)
    second_colors = browser_actions.get_all_colors_in_element(second_button)

    assert not are_lists_different(len(first_colors), len(first_ref_colors))
    assert are_lists_different(len(second_colors), len(second_ref_colors))

    # Going back moves the highlight to the first match again
    find_toolbar.previous_match()
    first_colors = browser_actions.get_all_colors_in_element(first_button)
    second_colors = browser_actions.get_all_colors_in_element(second_button)

    assert are_lists_different(len(first_colors), len(first_ref_colors))
    assert not are_lists_different(len(second_colors), len(second_ref_colors))
