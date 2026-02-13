from typing import Literal

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ReaderView
from modules.components.dropdown import Dropdown
from modules.page_object import GenericPage
from modules.util import Utilities


@pytest.fixture()
def test_case() -> str:
    return "130919"


# Constants / parametrization
READER_VIEW_URL: str = (
    "https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages"
)

SizeControl = Literal["minus", "plus"]
AlignKey = Literal["left", "right", "center"]
AlignCSS = Literal["start", "right", "center"]
SliderDirection = Literal["decrease", "increase"]

SIZE_CONTROLS: list[SizeControl] = ["minus", "plus"]
FONTS: list[Literal["sans-serif", "serif", "monospace"]] = [
    "sans-serif",
    "serif",
    "monospace",
]
ALIGNMENTS: list[tuple[AlignKey, AlignCSS]] = [
    ("left", "start"),
    ("right", "right"),
    ("center", "center"),
]
SLIDER_DIRS: list[SliderDirection] = ["decrease", "increase"]


# Helpers
def _open_reader_type_panel(web_page: GenericPage, reader_view: ReaderView) -> None:
    """
    Open the target page, enter Reader View, and open the 'Type' panel.
    """
    web_page.open()
    reader_view.open_reader_view_searchbar()
    reader_view.click_toolbar_option("toolbar-type")


def _css_int(util: Utilities, element, prop: str) -> int:
    """
    Read a CSS property and normalize it to an integer by stripping non-numeric chars.
    """
    return int(util.remove_all_non_numbers(element.value_of_css_property(prop)))


@pytest.mark.parametrize("font", FONTS)
def test_type_control_panel_font(
    driver: Firefox, font: Literal["sans-serif", "serif", "monospace"]
) -> None:
    """
    C130919.1: Ensure the functionality of the type control panels works (font family).
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    _open_reader_type_panel(web_page, reader_view)

    body = web_page.get_element("page-body")

    # Ensure default is sans-serif first so the next wait has a stable baseline
    reader_view.wait.until(
        lambda _: "sans-serif" in body.value_of_css_property("font-family")
    )

    font_dropdown_root = reader_view.get_element("toolbar-font-selector")
    font_dropdown = Dropdown(
        page=reader_view, require_shadow=False, root=font_dropdown_root
    )
    font_dropdown.select_option(
        f"about-reader-font-type-{font}",
        option_tag="option",
        label_name="data-l10n-id",
    )

    reader_view.wait.until(lambda _: font in body.value_of_css_property("font-family"))


@pytest.mark.parametrize("control", SIZE_CONTROLS)
def test_type_control_panel_size(driver: Firefox, control: SizeControl) -> None:
    """
    C130919.2: Ensure the functionality of the type control panels works (text size).
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    _open_reader_type_panel(web_page, reader_view)

    body = web_page.get_element("page-body")
    size_before = _css_int(util, body, "--font-size")

    reader_view.get_element(f"toolbar-textsize-{control}").click()

    if control == "minus":
        reader_view.wait.until(
            lambda _: _css_int(util, body, "--font-size") < size_before
        )
    else:
        reader_view.wait.until(
            lambda _: _css_int(util, body, "--font-size") > size_before
        )


@pytest.mark.parametrize("alignment,intended_alignment", ALIGNMENTS)
def test_type_control_panel_text_alignment(
    driver: Firefox,
    alignment: AlignKey,
    intended_alignment: AlignCSS,
) -> None:
    """
    C130919.3: Ensure the functionality of the type control panels works (text alignment).
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)

    _open_reader_type_panel(web_page, reader_view)

    container = web_page.get_element("container-div")
    reader_view.open_advanced_options()

    reader_view.get_element(f"toolbar-text-align-{alignment}").click()
    reader_view.wait.until(
        lambda _: (
            container.value_of_css_property("--text-alignment") == intended_alignment
        )
    )


@pytest.mark.parametrize("direction", SLIDER_DIRS)
def test_type_control_panel_content_width(
    driver: Firefox, direction: SliderDirection
) -> None:
    """
    C130919.4: Ensure the functionality of the type control panels works (content width slider).
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    _open_reader_type_panel(web_page, reader_view)

    reader_view.change_slider_element_shadow_parent("toolbar-content-width")

    body = web_page.get_element("page-body")
    width_before = _css_int(util, body, "--content-width")
    slider = reader_view.get_element("slider")

    reader_view.change_slider_value(slider, increase=(direction == "increase"))

    if direction == "decrease":
        reader_view.wait.until(
            lambda _: _css_int(util, body, "--content-width") < width_before
        )
    else:
        reader_view.wait.until(
            lambda _: _css_int(util, body, "--content-width") > width_before
        )


@pytest.mark.parametrize("direction", SLIDER_DIRS)
def test_type_control_panel_line_spacing(
    driver: Firefox, direction: SliderDirection
) -> None:
    """
    C130919.5: Ensure the functionality of the type control panels works (line spacing slider).
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    _open_reader_type_panel(web_page, reader_view)

    reader_view.change_slider_element_shadow_parent("toolbar-line-spacing")

    body = web_page.get_element("page-body")
    block_before = _css_int(util, body, "block-size")
    slider = reader_view.get_element("slider")

    reader_view.change_slider_value(slider, increase=(direction == "increase"))

    if direction == "decrease":
        reader_view.wait.until(
            lambda _: _css_int(util, body, "block-size") < block_before
        )
    else:
        reader_view.wait.until(
            lambda _: _css_int(util, body, "block-size") > block_before
        )


def test_type_control_panel_character_spacing(driver: Firefox) -> None:
    """
    C130919.6: Ensure the functionality of the type control panels works (character spacing slider).
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    _open_reader_type_panel(web_page, reader_view)
    reader_view.open_advanced_options()

    reader_view.change_slider_element_shadow_parent("toolbar-character-spacing")

    container = web_page.get_element("container-div")
    letter_before = _css_int(util, container, "--letter-spacing")
    slider = reader_view.get_element("slider")

    reader_view.change_slider_value(slider, increase=True)

    reader_view.wait.until(
        lambda _: _css_int(util, container, "--letter-spacing") > letter_before
    )


def test_type_control_panel_word_spacing(driver: Firefox) -> None:
    """
    C130919.7: Ensure the functionality of the type control panels works (word spacing slider).
    """
    web_page = GenericPage(driver, url=READER_VIEW_URL)
    reader_view = ReaderView(driver)
    util = Utilities()

    _open_reader_type_panel(web_page, reader_view)
    reader_view.open_advanced_options()

    reader_view.change_slider_element_shadow_parent("toolbar-word-spacing")

    container = web_page.get_element("container-div")
    word_before = _css_int(util, container, "--word-spacing")
    slider = reader_view.get_element("slider")

    reader_view.change_slider_value(slider, increase=True)

    reader_view.wait.until(
        lambda _: _css_int(util, container, "--word-spacing") > word_before
    )
