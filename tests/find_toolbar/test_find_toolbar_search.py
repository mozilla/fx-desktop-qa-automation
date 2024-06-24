import logging
from typing import Callable

import pytest
from PIL import Image
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import FindToolbar

TARGET_LINK = "about:telemetry"


def test_find_toolbar_search(driver: Firefox, screenshot: Callable):
    driver.get("about:about")
    find_toolbar = FindToolbar(driver).open()
    find_toolbar.find(TARGET_LINK[6:12])

    target_link_el = driver.find_element(By.CSS_SELECTOR, f"a[href='{TARGET_LINK}']")
    image_loc = screenshot("ref")

    # Get browser window size and scroll position
    scroll_position = driver.execute_script(
        "return { x: window.scrollX, y: window.scrollY };"
    )

    # Get device pixel ratio
    device_pixel_ratio = driver.execute_script("return window.devicePixelRatio;")

    link_loc = target_link_el.location
    link_size = target_link_el.size
    x_start = int((link_loc["x"] - scroll_position["x"]) * device_pixel_ratio)
    y_start = int((link_loc["y"] - scroll_position["y"]) * device_pixel_ratio)

    x_end = x_start + int(link_size["width"] * device_pixel_ratio)
    logging.info(f"{x_start}, {y_start}")

    shot_image = Image.open(image_loc)
    colorset = set(
        [shot_image.getpixel((x, y_start + 7)) for x in range(x_start, x_end)]
    )

    for x in range(x_start, x_end):
        loc = (x, y_start + 7)
        pixel = shot_image.getpixel(loc)
        logging.info(f"{loc}: {pixel}")
    # logging.info(colorset)
