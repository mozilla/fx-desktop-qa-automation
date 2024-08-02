import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.page_object import AboutPrefs, GenericPage
from modules.util import Utilities

size_controllers = ["minus", "plus"]
themes = [
    ("light", "rgb(255, 255, 255)"),
    ("dark", "rgb(28, 27, 34)"),
    ("sepia", "rgb(244, 236, 216)"),
]
fonts = ["sans-serif", "serif", "monospace"]
alignments = [("left", "start"), ("right", "right"), ("center", "center")]


READER_VIEW_URL = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)


def prep_test(web_page: GenericPage, reader_view: ReaderView) -> None:
    web_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.click_toolbar_option("toolbar-type")


@pytest.mark.parametrize("font", fonts)
def test_type_control_panel_font(driver: Firefox, font: str):
    """
    C130919: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    prep_test(web_page, reader_view)

    body = web_page.get_element("body")

    reader_view.wait.until(
        lambda _: "sans-serif" in body.value_of_css_property("font-family")
    )
    font_dropdown_root = reader_view.get_element("toolbar-font-selector")
    font_dropdown = AboutPrefs(driver).Dropdown(
        page=reader_view, require_shadow=False, root=font_dropdown_root
    )
    font_dropdown.select_option(
        f"about-reader-font-type-{font}", option_tag="option", label_name="data-l10n-id"
    )
    reader_view.wait.until(lambda _: font in body.value_of_css_property("font-family"))


@pytest.mark.parametrize("type", size_controllers)
def test_type_control_panel_size(driver: Firefox, type: str):
    """
    C130919: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    prep_test(web_page, reader_view)

    body = web_page.get_element("body")
    font_before = int(
        util.remove_all_non_numbers(body.value_of_css_property("--font-size"))
    )
    reader_view.get_element(f"toolbar-textsize-{type}").click()
    if type == "minus":
        reader_view.wait.until(
            lambda _: int(
                util.remove_all_non_numbers(body.value_of_css_property("--font-size"))
            )
            < font_before
        )
    else:
        reader_view.wait.until(
            lambda _: int(
                util.remove_all_non_numbers(body.value_of_css_property("--font-size"))
            )
            > font_before
        )


@pytest.mark.parametrize("alignment, intended_alignment", alignments)
def test_type_control_panel_text_alignment(
    driver: Firefox, alignment: str, intended_alignment: str
):
    """
    C130919: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    web_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.click_toolbar_option("toolbar-type")

    container = web_page.get_element("container-div")
    reader_view.open_advanced_options()

    reader_view.get_element(f"toolbar-text-align-{alignment}").click()
    reader_view.wait.until(
        lambda _: container.value_of_css_property("--text-alignment")
        == intended_alignment
    )
