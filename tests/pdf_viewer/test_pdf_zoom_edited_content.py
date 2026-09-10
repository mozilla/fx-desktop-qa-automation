import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_TO_ADD = "PDF editor text"


@pytest.fixture()
def test_case():
    return "1938257"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def add_to_prefs_list():
    return [("pdfjs.annotationEditorMode", 0)]


def test_zoom_works_on_edited_pdf(pdf_viewer: GenericPdf):
    """C1938257: Verify that zoom in and out works on an edited PDF."""
    # Step 1: PDF is open and the editor tools are available.
    pdf_viewer.element_visible("toolbar-text")
    pdf_viewer.element_visible("toolbar-draw")

    # Steps 2-3: Add text, zoom in and out, and verify the text remains.
    pdf_viewer.select_editor_tool("toolbar-text")
    pdf_viewer.add_text_to_pdf_page(TEXT_TO_ADD)
    pdf_viewer.actions.send_keys(Keys.ESCAPE).send_keys(Keys.ESCAPE).perform()

    initial_scale = float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
    pdf_viewer.zoom_in_toolbar()
    pdf_viewer.expect_scale_factor_greater_than(initial_scale)
    pdf_viewer.element_has_text("added-text", TEXT_TO_ADD)

    zoomed_in_scale = float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(zoomed_in_scale)
    pdf_viewer.element_has_text("added-text", TEXT_TO_ADD)

    # Steps 4-5: Add a drawing, zoom in and out, and verify it remains.
    pdf_viewer.jump_to_page(2)
    pdf_viewer.clear_cache()
    pdf_viewer.select_editor_tool("toolbar-draw")
    pdf_viewer.draw_on_pdf_page("2", y_offset=-150)

    initial_scale = float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
    pdf_viewer.zoom_in_toolbar()
    pdf_viewer.expect_scale_factor_greater_than(initial_scale)
    pdf_viewer.element_exists("added-drawing")

    zoomed_in_scale = float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(zoomed_in_scale)
    pdf_viewer.element_exists("added-drawing")
