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


def test_open_pdf_in_fx(driver: Firefox, pdf_file_path: str):
    """
    C936503: PDF files can be successfully opened in Firefox

    Arguments:
        pdf_file_path: pdf file directory path
    """

    file_url = f"file://{pdf_file_path}"
    pdf = GenericPdf(driver, pdf_url=file_url)
    pdf.open()

    # Verify that the PDF viewer is loaded
    pdf.url_contains("pdf")
    pdf.title_contains(PDF_FILE_NAME)
