import pytest
from selenium.webdriver.support.color import Color

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_TO_ADD = "PDF editor text"
INITIAL_COLOR = "#0060df"
INITIAL_FONT_SIZE = 24
UPDATED_COLOR = "#ff0039"
UPDATED_FONT_SIZE = 12


@pytest.fixture()
def test_case():
    return "1938269"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def _assert_text_style(pdf_viewer: GenericPdf, color: str, font_size: int) -> None:
    scale = float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
    expected_size = pytest.approx(font_size * scale, abs=0.01)

    def text_style_matches(_):
        current_style = pdf_viewer.get_pdf_text_style()
        return (
            Color.from_string(current_style["color"]).hex == color
            and float(current_style["font_size"].removesuffix("px")) == expected_size
        )

    pdf_viewer.wait.until(
        text_style_matches,
        message=f"Expected PDF text color {color} and rendered size {font_size * scale}px.",
    )
    style = pdf_viewer.get_pdf_text_style()
    assert Color.from_string(style["color"]).hex == color, (
        f"Expected PDF text color {color}, got {style['color']}."
    )
    assert float(style["font_size"].removesuffix("px")) == expected_size, (
        f"Expected PDF text size {font_size}, got {style['font_size']}."
    )


def test_pdf_text_uses_selected_font_size_and_color(pdf_viewer: GenericPdf):
    """C1938269: New and existing PDF text use the selected font size and color."""
    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.element_visible("text-options")
    pdf_viewer.set_pdf_text_style(INITIAL_COLOR, INITIAL_FONT_SIZE)

    pdf_viewer.add_text_to_pdf_page(TEXT_TO_ADD)
    _assert_text_style(pdf_viewer, INITIAL_COLOR, INITIAL_FONT_SIZE)

    pdf_viewer.select_pdf_text_area()
    pdf_viewer.element_visible("text-options")
    pdf_viewer.set_pdf_text_style(UPDATED_COLOR, UPDATED_FONT_SIZE)
    _assert_text_style(pdf_viewer, UPDATED_COLOR, UPDATED_FONT_SIZE)
    assert pdf_viewer.get_element("added-text-content").text == TEXT_TO_ADD, (
        "Changing PDF text style must preserve the written text."
    )
