import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"


@pytest.fixture()
def test_case():
    return "936503"


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_open_pdf_in_fx(driver: Firefox, pdf_viewer: GenericPdf):
    """
    C936503: PDF files can be successfully opened in Firefox

    Arguments:
        pdf_viewer: instance of GenericPdf with correct path.
    """
    # Verify that the PDF viewer is loaded
    pdf_viewer.url_contains("pdf")
    pdf_viewer.title_contains(PDF_FILE_NAME)
