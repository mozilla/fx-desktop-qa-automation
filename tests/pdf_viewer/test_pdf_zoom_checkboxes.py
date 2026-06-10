import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
CHECKBOX = "first-checkbox"


@pytest.fixture()
def test_case():
    return "1018756"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_zoom_works_on_checkboxes(pdf_viewer: GenericPdf):
    """
    C1018756: Verify that zoom works on checkboxes
    """
    # Step 1: PDF form with checkboxes is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(CHECKBOX)

    # Step 2: Click over any checkbox and verify the checkbox status is updated.
    checkbox = pdf_viewer.select_and_return_checkbox(CHECKBOX)
    pdf_viewer.element_selected(CHECKBOX)

    # Step 3: Zoom in the page and verify there are no unexpected issues with the form.
    before_zoom_in_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_in_toolbar()
    pdf_viewer.expect_scale_factor_greater_than(before_zoom_in_scale_factor)
    pdf_viewer.expect(lambda _: checkbox.is_selected())

    # Step 4: Zoom out a couple of times and verify there are no unexpected issues with the form.
    before_first_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(before_first_zoom_out_scale_factor)
    pdf_viewer.expect(lambda _: checkbox.is_selected())

    before_second_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(before_second_zoom_out_scale_factor)
    pdf_viewer.expect(lambda _: checkbox.is_selected())
