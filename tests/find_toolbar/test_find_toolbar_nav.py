import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import FindToolbar
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "127249"


# The number of colors that can be different between two images
# before we call them different color schemes
TOLERANCE = 3

TARGET_PAGE = "about:about"
DELETE_PROFILE_SELECTOR = "a[href='about:deleteprofile']"
PROCESSES_SELECTOR = "a[href='about:processes']"

first_match = (By.CSS_SELECTOR, DELETE_PROFILE_SELECTOR)
fourth_match = (By.CSS_SELECTOR, PROCESSES_SELECTOR)


def are_lists_different(a: int, b: int) -> bool:
    return abs(a - b) > TOLERANCE


def test_find_toolbar_navigation(
    driver: Firefox, find_toolbar: FindToolbar, browser_actions: BrowserActions
):
    """
    C127249: Navigate through found items

    Arguments:
        browser_actions: instantiation of BrowserActions BOM.
        find_toolbar: instantiation of FindToolbar BOM.
    """
    driver.get(TARGET_PAGE)

    find_toolbar.open()
    find_toolbar.find("pro")
    match_status = find_toolbar.match_dict
    assert match_status["total"] == 7

    # Sometimes we get a match that isn't the first
    # (This also tests that the number is correct)
    find_toolbar.rewind_to_first_match()

    # Ensure that first match is highlighted, others are not
    first_match_colors = browser_actions.get_all_colors_in_element(first_match)
    fourth_match_colors = browser_actions.get_all_colors_in_element(fourth_match)

    assert len(first_match_colors) > len(fourth_match_colors)
    assert are_lists_different(len(first_match_colors), len(fourth_match_colors))

    # Navigate with keyboard and button
    find_toolbar.navigate_matches_n_times(3)
    first_match_colors = browser_actions.get_all_colors_in_element(first_match)
    fourth_match_colors = browser_actions.get_all_colors_in_element(fourth_match)

    assert len(first_match_colors) < len(fourth_match_colors)
    assert are_lists_different(len(first_match_colors), len(fourth_match_colors))

    # Check what happens when you go past the last match
    find_toolbar.rewind_to_first_match()
    find_toolbar.navigate_matches_n_times(find_toolbar.match_dict["total"])
    find_toolbar.element_visible("reached-bottom-label")

    # ...And hit Previous on the first match
    find_toolbar.previous_match()
    find_toolbar.element_visible("reached-top-label")
