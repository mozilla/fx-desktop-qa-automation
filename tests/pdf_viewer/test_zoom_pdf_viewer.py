import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf
from modules.browser_object import PdfViewer

controls = [
    "out",
    "in"
]


@pytest.mark.parametrize("control", controls)
def test_zoom_pdf_viewer(driver: Firefox, fillable_pdf_url: str, control: str):
    """
    C3928: ensure that in the pdf viewer you can zoom in and out
    """
    pdf_view = PdfViewer(driver)
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url).open()

    body = pdf_page.get_element("body")
    before_scale_factor = float(body.value_of_css_property("--scale-factor"))

    pdf_view.get_element(f"zoom-{control}").click()
    if control == "out":
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor")) < before_scale_factor
        )
    else:
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor")) > before_scale_factor
        )