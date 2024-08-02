import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PdfViewer
from modules.page_object import GenericPdf

controls = ["out", "in"]


@pytest.mark.parametrize("control", controls)
def test_zoom_pdf_viewer_toolbar(driver: Firefox, fillable_pdf_url: str, control: str):
    """
    C3928: ensure that in the pdf viewer you can zoom in and out
    """
    pdf_view = PdfViewer(driver)
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url).open()

    body = pdf_page.get_element("body")
    before_scale_factor = float(body.value_of_css_property("--scale-factor"))

    if control == "out":
        pdf_view.zoom_out_toolbar()
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            < before_scale_factor
        )
    else:
        pdf_view.zoom_in_toolbar()
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            > before_scale_factor
        )


@pytest.mark.parametrize("control", controls)
def test_zoom_pdf_viewer_keys(driver: Firefox, fillable_pdf_url: str, control: str):
    """
    C3928: ensure that in the pdf viewer you can zoom in and out
    """
    pdf_view = PdfViewer(driver)
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url).open()

    body = pdf_page.get_element("body")
    before_scale_factor = float(body.value_of_css_property("--scale-factor"))

    pdf_view.get_element(f"zoom-{control}").click()
    if control == "out":
        pdf_view.zoom_out_keys()
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            < before_scale_factor
        )
    else:
        pdf_view.zoom_in_keys()
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            > before_scale_factor
        )
