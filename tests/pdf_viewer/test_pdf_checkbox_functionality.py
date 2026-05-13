import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"


@pytest.fixture()
def test_case():
    return "1017491"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_checkboxes_work_correctly(pdf_viewer: GenericPdf):
    """
    C1017491: Verify that the checkboxes work correctly
    """
    # Step 1: PDF form with checkboxes is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible("first-checkbox")

    # Step 2: Click on any checkbox from the PDF form.
    checkbox = pdf_viewer.select_and_return_checkbox("first-checkbox")
    pdf_viewer.element_selected("first-checkbox")

    # Step 3: Click away from the checkbox and verify the checkbox status remains the same.
    pdf_viewer.click_on("pdf-body")
    pdf_viewer.expect(lambda _: checkbox.is_selected())
