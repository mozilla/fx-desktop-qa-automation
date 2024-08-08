import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import GenericPage

themes = [
    ("light", "rgb(255, 255, 255)"),
    ("dark", "rgb(28, 27, 34)"),
    ("sepia", "rgb(244, 236, 216)"),
    ("contrast", "rgb(0, 0, 0)"),
    ("gray", "rgb(215, 215, 219)")
]

READER_VIEW_URL = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)


@pytest.mark.parametrize("theme, intended_color", themes)
def test_reader_view_theme_panel(driver: Firefox, theme: str, intended_color: str):
    """
    C2637622.1: Ensuring that the themes work as expected in reader view
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    web_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.click_toolbar_option("toolbar-theme")

    body = web_page.get_element("body")
    reader_view.get_element(f"toolbar-theme-{theme}").click()

    reader_view.wait.until(
        lambda _: body.value_of_css_property("background-color") == intended_color
    )