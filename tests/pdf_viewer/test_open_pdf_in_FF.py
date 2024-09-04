from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "936503"


@pytest.fixture()
def temp_pdf(tmp_path):
    loc = tmp_path / "i-9.pdf"
    copyfile("data/i-9.pdf", loc)
    return loc


def test_open_pdf_in_fx(driver: Firefox, temp_pdf):
    """
    C936503: PDF files can be successfully opened in Firefox
    """

    file_url = f"file://{temp_pdf}"
    pdf = GenericPdf(driver, pdf_url=file_url)
    pdf.open()

    # Verify that the PDF viewer is loaded
    pdf.url_contains("pdf")
    pdf.title_contains("i-9.pdf")
