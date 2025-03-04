import logging

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import FindToolbar
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "127239"


# The number of colors that can be different between two images
# before we call them different color schemes
TOLERANCE = 3

TARGET_PAGE = "about:about"
TARGET_LINK = "about:telemetry"

selector = (By.CSS_SELECTOR, f"a[href='{TARGET_LINK}']")


def are_lists_different(a: int, b: int) -> bool:
    return abs(a - b) > TOLERANCE


@pytest.mark.ci
def test_find_toolbar_search(
    driver: Firefox, find_toolbar: FindToolbar, browser_actions: BrowserActions
):
    """
    C127239: Perform a search (using the Find Toolbar)

    Arguments:
        browser_actions: instantiation of BrowserActions BOM.
        find_toolbar: instantiation of FindToolbar BOM.
    """
    driver.get(TARGET_PAGE)
    # Check highlighting: get a reference for what colors are in the link before
    ref_colors = browser_actions.get_all_colors_in_element(selector)

    # Search part of the target text
    find_toolbar.open()
    find_toolbar.find(TARGET_LINK[6:12])

    # Check highlighting: get the list of colors that are in the link after hit
    target_colors = browser_actions.get_all_colors_in_element(selector)

    # Should be more colors after we highlight part of the word
    logging.info(f"{len(target_colors)}, {len(ref_colors)}")
    assert are_lists_different(len(target_colors), len(ref_colors))

    # Search for something where our target will no longer be the first hit
    driver.get(TARGET_PAGE)
    find_toolbar.find("about")

    # Confirm that our target is no longer highlighted by matching colors with reference
    cleared_colors = browser_actions.get_all_colors_in_element(selector)

    assert not are_lists_different(len(ref_colors), len(cleared_colors))
