import pytest

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


def test_pdf_text_uses_selected_font_size_and_color(pdf_viewer: GenericPdf):
    """C1938269: New and existing PDF text use the selected font size and color."""
    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.element_visible("text-options")
    pdf_viewer.set_pdf_text_style(INITIAL_COLOR, INITIAL_FONT_SIZE)

    pdf_viewer.add_text_to_pdf_page(TEXT_TO_ADD)
    scale = float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
    initial_style = pdf_viewer.get_pdf_text_style()
    assert initial_style["color"] == "rgb(0, 96, 223)", (
        f"Expected new PDF text to use {INITIAL_COLOR}, got {initial_style['color']}."
    )
    assert float(initial_style["font_size"].removesuffix("px")) == pytest.approx(
        INITIAL_FONT_SIZE * scale, abs=0.01
    ), (
        f"Expected new PDF text size {INITIAL_FONT_SIZE}, got {initial_style['font_size']}."
    )

    pdf_viewer.select_pdf_text_area()
    pdf_viewer.set_pdf_text_style(UPDATED_COLOR, UPDATED_FONT_SIZE)
    updated_style = pdf_viewer.get_pdf_text_style()
    assert updated_style["color"] == "rgb(255, 0, 57)", (
        f"Expected selected PDF text to use {UPDATED_COLOR}, got {updated_style['color']}."
    )
    assert float(updated_style["font_size"].removesuffix("px")) == pytest.approx(
        UPDATED_FONT_SIZE * scale, abs=0.01
    ), (
        f"Expected selected PDF text size {UPDATED_FONT_SIZE}, got {updated_style['font_size']}."
    )
    assert pdf_viewer.get_element("added-text-content").text == TEXT_TO_ADD, (
        "Changing PDF text style must preserve the written text."
    )
