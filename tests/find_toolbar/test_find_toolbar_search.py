import logging
from typing import Callable

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import FindToolbar
from modules.util import BrowserActions

TARGET_LINK = "about:telemetry"


def test_find_toolbar_search(driver: Firefox, screenshot: Callable):
    driver.get("about:about")
    ba = BrowserActions(driver)

    # Check highlighting: get a reference for what colors are in the link before
    ref_link_el = driver.find_element(By.CSS_SELECTOR, f"a[href='{TARGET_LINK}']")
    ref_image_loc = screenshot("ref")
    ref_colors = ba.get_all_colors_in_element(ref_link_el, ref_image_loc)

    # Search part of the target text
    find_toolbar = FindToolbar(driver).open()
    find_toolbar.find(TARGET_LINK[6:12])

    # Check highlighting: get the list of colors that are in the link after hilite
    target_link_el = driver.find_element(By.CSS_SELECTOR, f"a[href='{TARGET_LINK}']")
    target_image_loc = screenshot("test")
    target_colors = ba.get_all_colors_in_element(target_link_el, target_image_loc)

    # Should be more colors after we highlight part of the word
    assert len(target_colors) > len(ref_colors)
