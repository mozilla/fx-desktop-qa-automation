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
slider_options = ["decrease", "increase"]


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
    C130919.1: Ensure the functionality of the type control panels works
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
    C130919.2: Ensure the functionality of the type control panels works
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
    C130919.3: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    prep_test(web_page, reader_view)

    container = web_page.get_element("container-div")
    reader_view.open_advanced_options()

    reader_view.get_element(f"toolbar-text-align-{alignment}").click()
    reader_view.wait.until(
        lambda _: container.value_of_css_property("--text-alignment")
        == intended_alignment
    )

@pytest.mark.parametrize("width", slider_options)
def test_type_control_panel_content_width(
    driver: Firefox, width: str
):
    """
    C130919.4: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    prep_test(web_page, reader_view)

    body = web_page.get_element("body")
    before_content_width = int(util.remove_all_non_numbers(body.value_of_css_property("--content-width")))
    content_width_slider = reader_view.get_element("slider-content-width")

    if width == "decrease":
        reader_view.change_slider_value(content_width_slider, increase=False)
        reader_view.wait.until(
            lambda _: int(util.remove_all_non_numbers(body.value_of_css_property("--content-width"))) < before_content_width
        )
    else:
        reader_view.change_slider_value(content_width_slider)
        reader_view.wait.until(
            lambda _: int(util.remove_all_non_numbers(body.value_of_css_property("--content-width"))) > before_content_width
        )

@pytest.mark.parametrize("line_height", slider_options)
def test_type_control_panel_line_spacing(
    driver: Firefox, line_height: str
):
    """
    C130919.5: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    prep_test(web_page, reader_view)

    body = web_page.get_element("body")
    before_block_size = int(util.remove_all_non_numbers(body.value_of_css_property("block-size")))
    content_line_spacer_slider = reader_view.get_element("slider-line-spacing")

    if line_height == "decrease":
        reader_view.change_slider_value(content_line_spacer_slider, increase=False)
        reader_view.wait.until(
            lambda _: int(util.remove_all_non_numbers(body.value_of_css_property("block-size"))) < before_block_size
        )
    else:
        reader_view.change_slider_value(content_line_spacer_slider)
        reader_view.wait.until(
            lambda _: int(util.remove_all_non_numbers(body.value_of_css_property("block-size"))) > before_block_size
        )

def test_type_control_panel_character_spacing(
    driver: Firefox
):
    """
    C130919.6: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    prep_test(web_page, reader_view)
    reader_view.open_advanced_options()

    container = web_page.get_element("container-div")
    before_character_spacing = int(util.remove_all_non_numbers(container.value_of_css_property("--letter-spacing")))
    content_character_spacing_slider = reader_view.get_element("slider-character-spacing")
    reader_view.change_slider_value(content_character_spacing_slider)

    reader_view.wait.until(
        lambda _: int(util.remove_all_non_numbers(container.value_of_css_property("--letter-spacing"))) > before_character_spacing
    )

def test_type_control_panel_word_spacing(
    driver: Firefox
):
    """
    C130919.7: Ensure the functionality of the type control panels works
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    prep_test(web_page, reader_view)
    reader_view.open_advanced_options()

    container = web_page.get_element("container-div")
    before_word_spacing = int(util.remove_all_non_numbers(container.value_of_css_property("--word-spacing")))
    content_word_spacing_slider = reader_view.get_element("slider-word-spacing")
    reader_view.change_slider_value(content_word_spacing_slider)

    reader_view.wait.until(
        lambda _: int(util.remove_all_non_numbers(container.value_of_css_property("--word-spacing"))) > before_word_spacing
    )