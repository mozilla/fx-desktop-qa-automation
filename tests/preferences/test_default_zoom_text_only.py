from shutil import copyfile

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object import AboutPrefs

# Two local pages stand in for "several websites"
PAGE_FILENAMES = ["basic_webpage.html", "article_page.html"]
ZOOM_LEVELS = [50, 110, 150]
# Only this page has an image
IMAGE_PAGE = "basic_webpage.html"


@pytest.fixture()
def about_prefs_category():
    return "accessibility"


@pytest.fixture()
def test_case():
    return "3369716"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


@pytest.fixture()
def page_urls(tmp_path):
    """Copy the test pages to tmp_path and return their file:// URLs"""
    for filename in PAGE_FILENAMES:
        copyfile(f"data/pages/{filename}", tmp_path / filename)
    copyfile("data/goomy.png", tmp_path / "goomy.png")
    return [(tmp_path / filename).as_uri() for filename in PAGE_FILENAMES]


def _page_layout(driver: Firefox, has_image: bool) -> dict:
    """Sizes of the page, its image and its heading font"""
    layout = {
        "width": driver.find_element(By.TAG_NAME, "html").size["width"],
        "text": float(
            driver.find_element(By.TAG_NAME, "h2")
            .value_of_css_property("font-size")
            .removesuffix("px")
        ),
    }
    if has_image:
        layout["image"] = driver.find_element(By.TAG_NAME, "img").size["width"]
    return layout


def _is_close(actual: float, expected: float) -> bool:
    """Allow 5% wiggle room for rounding and scrollbars"""
    return abs(actual - expected) <= expected * 0.05


def _verify_text_zoom(
    driver: Firefox, about_prefs: AboutPrefs, handle: str, base: dict, zoom: int
):
    """Only the text grows or shrinks, the page and images stay the same"""
    driver.switch_to.window(handle)

    def _only_text_zoomed(d):
        layout = _page_layout(d, "image" in base)
        return (
            _is_close(layout["width"], base["width"])
            and ("image" not in base or _is_close(layout["image"], base["image"]))
            and _is_close(layout["text"], base["text"] * zoom / 100)
        )

    about_prefs.expect_in_content(_only_text_zoomed)


def test_default_zoom_text_only(
    driver: Firefox, about_prefs: AboutPrefs, page_urls: list[str]
):
    """
    C3369716 - With "Zoom text only" checked, the Default zoom only changes text size.
    """
    # Open each website in its own tab and save its sizes at 100%
    base_layouts = {}
    for index, url in enumerate(page_urls):
        if index > 0:
            about_prefs.open_and_switch_to_new_window("tab")
        driver.get(url)
        base_layouts[driver.current_window_handle] = _page_layout(
            driver, url.endswith(IMAGE_PAGE)
        )

    # Settings goes in the last tab
    about_prefs.open_and_switch_to_new_window("tab")
    about_prefs.open()
    settings_handle = driver.current_window_handle
    about_prefs.click_zoom_text_only()

    for zoom in ZOOM_LEVELS:
        driver.switch_to.window(settings_handle)
        about_prefs.set_default_zoom_level(zoom)

        # Every website only zooms its text
        for handle, base in base_layouts.items():
            _verify_text_zoom(driver, about_prefs, handle, base, zoom)
