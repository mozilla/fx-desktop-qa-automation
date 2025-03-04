import pytest
from selenium.webdriver import Firefox

from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "3928"


controls = ["out", "in"]


@pytest.mark.parametrize("control", controls)
def test_zoom_pdf_viewer_toolbar(driver: Firefox, pdf_viewer: GenericPdf, control: str):
    """
    C3928: ensure that in the pdf viewer you can zoom in and out

    Arguments:
        control: zoom controls
        pdf_viewer: instance of GenericPdf with correct path.
    """
    zoom_pdf_viewer(pdf_viewer, control, "Tools")


@pytest.mark.parametrize("control", controls)
def test_zoom_pdf_viewer_keys(driver: Firefox, pdf_viewer: GenericPdf, control: str):
    """
    C3928: ensure that in the pdf viewer you can zoom in and out

    Arguments:
        control: zoom controls
        pdf_viewer: instance of GenericPdf with correct path.
    """
    zoom_pdf_viewer(pdf_viewer, control, "Keys")


def zoom_pdf_viewer(pdf_viewer: GenericPdf, control: str, input_type: str):
    """
    zoom base function to change based on input_type

    Arguments:
        control: zoom controls
        pdf_viewer: instance of GenericPdf with correct path.
        input_type: Keys or Tool
    """
    pdf_zoom = {
        "zoom_out": pdf_viewer.zoom_out_keys
        if input_type == "Keys"
        else pdf_viewer.zoom_out_toolbar,
        "zoom_in": pdf_viewer.zoom_in_keys
        if input_type == "Keys"
        else pdf_viewer.zoom_in_toolbar,
    }
    body = pdf_viewer.get_element("pdf-body")
    before_scale_factor = float(body.value_of_css_property("--scale-factor"))

    if control == "out":
        pdf_zoom["zoom_out"]()
        pdf_viewer.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            < before_scale_factor
        )
        assert float(body.value_of_css_property("--scale-factor")) < before_scale_factor
    else:
        pdf_zoom["zoom_in"]()
        pdf_viewer.wait.until(
            lambda _: float(body.value_of_css_property("--scale-factor"))
            > before_scale_factor
        )
        assert float(body.value_of_css_property("--scale-factor")) > before_scale_factor
