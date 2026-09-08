import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
INITIAL_COLOR = "#0060df"
INITIAL_THICKNESS = 5
INITIAL_OPACITY = 0.5
UPDATED_COLOR = "#ff0039"
UPDATED_THICKNESS = 10
UPDATED_OPACITY = 0.75


@pytest.fixture()
def test_case():
    return "1938262"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_pdf_draw_color_thickness_and_opacity(pdf_viewer: GenericPdf):
    """
    C1938262: Verify drawing and an existing drawing use the selected color,
    thickness, and opacity.
    """
    # Step 1: PDF is opened and the Text/Draw toolbar buttons are available.
    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")

    # Steps 2-5: Select Draw and configure its color, thickness, and opacity.
    pdf_viewer.select_editor_tool("toolbar-draw")
    pdf_viewer.element_visible("draw-options")
    pdf_viewer.set_draw_style(INITIAL_COLOR, INITIAL_THICKNESS, INITIAL_OPACITY)

    # Step 6: Draw an element and verify that it uses the selected style.
    pdf_viewer.draw_on_pdf_page()
    initial_style = pdf_viewer.get_drawing_style()
    assert initial_style["color"] == INITIAL_COLOR
    assert float(initial_style["opacity"]) == INITIAL_OPACITY

    # Step 7: Select the drawing, change its style, and verify the update.
    pdf_viewer.select_drawing_area()
    pdf_viewer.element_visible("draw-options")
    pdf_viewer.set_draw_style(UPDATED_COLOR, UPDATED_THICKNESS, UPDATED_OPACITY)
    updated_style = pdf_viewer.get_drawing_style()

    assert updated_style["color"] == UPDATED_COLOR
    assert updated_style["thickness"] != initial_style["thickness"]
    assert float(updated_style["opacity"]) == UPDATED_OPACITY
