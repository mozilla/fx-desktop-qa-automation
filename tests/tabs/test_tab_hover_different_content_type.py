import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutPrefs

PDF_URL = "https://www.w3.org/WAI/WCAG21/Techniques/pdf/img/table-word.pdf"
VIDEO_URL = "https://www.w3schools.com/html/mov_bbb.mp4"
ANIMATION_URL = "https://css-tricks.com/examples/ShapesOfCSS/"
GRAPHICS_URL = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"

CONTENT_URLS = [PDF_URL, VIDEO_URL, ANIMATION_URL, GRAPHICS_URL]


@pytest.fixture()
def test_case():
    return "2693898"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.hoverPreview.enabled", True)]


def test_tab_hover_different_content_type(driver: Firefox):
    """
    C2693898: Verify that tab hover preview is displayed for tabs with different content types (PDF, video,
    animation, graphics).
    """
    # Instantiate objects
    tabs = TabBar(driver)
    about_prefs = AboutPrefs(driver, category="general")

    # Open tabs with different content types
    tabs.open_urls_in_tabs(CONTENT_URLS, open_first_in_current_tab=True)

    # Switch back to the first tab
    driver.switch_to.window(driver.window_handles[0])

    # Get the total number of tabs opened
    total_tabs = len(driver.window_handles)

    # Verify preview with Name, URL and Thumbnail is displayed for each content type
    tabs.verify_hover_preview(total_tabs)

    # Go to about:preferences and uncheck "Show an image preview when you hover on a tab"
    about_prefs.open()
    about_prefs.find_in_settings("show an image preview")
    about_prefs.click_on("tab-hover-preview-checkbox")

    # Verify preview shows Name and URL only (no Thumbnail)
    tabs.verify_hover_preview(total_tabs, expect_thumbnail=False)
