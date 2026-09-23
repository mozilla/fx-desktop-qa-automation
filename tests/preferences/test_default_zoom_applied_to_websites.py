from shutil import copyfile

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.page_object import AboutPrefs

# Two local pages stand in for "several websites"
PAGE_FILENAMES = ["basic_webpage.html", "article_page.html"]
ZOOM_LEVELS = [50, 110, 150]


@pytest.fixture()
def about_prefs_category():
    return "accessibility"


@pytest.fixture()
def test_case():
    return "3369712"


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


def _page_width(driver: Firefox) -> int:
    """Page width in CSS pixels, which shrinks as zoom grows"""
    return driver.find_element(By.TAG_NAME, "html").size["width"]


def _verify_zoom(driver: Firefox, handle: str, base_width: int, zoom: int):
    """Check the tab's page width matches the zoom level"""
    driver.switch_to.window(handle)
    expected = base_width * 100 / zoom
    AboutPrefs(driver).expect_in_content(
        lambda d: abs(_page_width(d) - expected) <= expected * 0.05
    )


def test_default_zoom_applied_to_websites(
    driver: Firefox, about_prefs: AboutPrefs, page_urls: list[str]
):
    """
    C3369712 - The Default zoom level is applied to all websites.
    """
    # Open each website in its own tab
    driver.get(page_urls[0])
    for url in page_urls[1:]:
        about_prefs.open_and_switch_to_new_window("tab")
        driver.get(url)

    # Settings goes in the last tab
    about_prefs.open_and_switch_to_new_window("tab")
    about_prefs.open()
    handles = driver.window_handles
    base_width = _page_width(driver)

    for zoom in ZOOM_LEVELS:
        driver.switch_to.window(handles[-1])
        about_prefs.set_default_zoom_level(zoom)

        # Settings and every website use the new zoom
        for handle in reversed(handles):
            _verify_zoom(driver, handle, base_width, zoom)
