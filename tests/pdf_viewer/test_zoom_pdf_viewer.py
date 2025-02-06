import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3928"


controls = ["out", "in"]


@pytest.mark.parametrize("control", controls)
def test_zoom_pdf_viewer_toolbar(driver: Firefox, fillable_pdf_url: str, control: str):
    """
    C3928: ensure that in the pdf viewer you can zoom in and out

    Arguments:
        control: zoom controls
        fillable_pdf_url: pdf file directory path
    """
    zoom_pdf_viewer(driver, fillable_pdf_url, control, "Tools")


@pytest.mark.parametrize("control", controls)
def test_zoom_pdf_viewer_keys(driver: Firefox, fillable_pdf_url: str, control: str):
    """
    C3928: ensure that in the pdf viewer you can zoom in and out

    Arguments:
        control: zoom controls
        fillable_pdf_url: pdf file directory path
    """
    zoom_pdf_viewer(driver, fillable_pdf_url, control, "Keys")


def zoom_pdf_viewer(
    driver: Firefox, fillable_pdf_url: str, control: str, input_type: str
):
    """
    zoom base function to change based on input_type

    Arguments:
        driver: Firefox webdriver
        control: zoom controls
        fillable_pdf_url: pdf file directory path
        input_type: Keys or Tool
    """
    pdf_page = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    pdf_zoom = {
        "zoom_out": pdf_page.zoom_out_keys
        if input_type == "Keys"
        else pdf_page.zoom_out_toolbar,
        "zoom_in": pdf_page.zoom_in_keys
        if input_type == "Keys"
        else pdf_page.zoom_in_toolbar,
    }
    body = pdf_page.get_element("pdf-body")
    before_scale_factor = float(body.value_of_css_property("--scale-factor"))

    if control == "out":
        pdf_zoom["zoom_out"]()
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            < before_scale_factor
        )
        assert float(body.value_of_css_property("--scale-factor")) < before_scale_factor
    else:
        pdf_zoom["zoom_in"]()
        pdf_page.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            > before_scale_factor
        )
        assert float(body.value_of_css_property("--scale-factor")) > before_scale_factor
