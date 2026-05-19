import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TEXT_FIELD = "first-name-field"
TEST_TEXT = "John Doe"


@pytest.fixture()
def test_case():
    return "1018755"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_zoom_works_on_text_fields(pdf_viewer: GenericPdf):
    """
    C1018755: Verify that zoom works on text fields
    """
    # Step 1: PDF form with text fields is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(TEXT_FIELD)

    # Step 2: Click and type inside the text field for the name section.
    pdf_viewer.fill(TEXT_FIELD, TEST_TEXT, press_enter=False)
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", TEST_TEXT)

    # Step 3: Zoom in the page and verify there are no unexpected issues with the form.
    before_zoom_in_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_in_toolbar()
    pdf_viewer.wait.until(
        lambda _: float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
        > before_zoom_in_scale_factor
    )
    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", TEST_TEXT)

    # Step 4: Zoom out a couple of times and verify there are no unexpected issues with the form.
    before_first_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.wait.until(
        lambda _: float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
        < before_first_zoom_out_scale_factor
    )

    before_second_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.wait.until(
        lambda _: float(pdf_viewer.pdf_body.value_of_css_property("--scale-factor"))
        < before_second_zoom_out_scale_factor
    )

    pdf_viewer.element_attribute_is(TEXT_FIELD, "value", TEST_TEXT)
