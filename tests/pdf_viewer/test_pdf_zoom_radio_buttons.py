import pytest

from modules.page_object import GenericPdf

PDF_FILE_NAME = "interactiveform_enabled.pdf"
RADIO_BUTTON = "radio-button"


@pytest.fixture()
def test_case():
    return "1018757"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


@pytest.fixture()
def temp_selectors():
    return {
        RADIO_BUTTON: {
            "selectorData": "input[type='radio']",
            "strategy": "css",
            "groups": [],
        }
    }


def test_pdf_zoom_works_on_radio_buttons(
    pdf_viewer: GenericPdf,
    temp_selectors,
):
    """
    C1018757: Verify that zoom works on radio buttons
    """
    pdf_viewer.elements |= temp_selectors

    # Step 1: PDF form with radio buttons is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(RADIO_BUTTON)

    # Step 2: Click on any radio button and verify selection is made.
    pdf_viewer.click_on(RADIO_BUTTON)
    pdf_viewer.element_selected(RADIO_BUTTON)

    # Step 3: Zoom in the page and verify there are no unexpected issues with the form.
    before_zoom_in_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_in_toolbar()
    pdf_viewer.expect_scale_factor_greater_than(before_zoom_in_scale_factor)
    pdf_viewer.element_selected(RADIO_BUTTON)

    # Step 4: Zoom out a couple of times and verify there are no unexpected issues with the form.
    before_first_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(before_first_zoom_out_scale_factor)
    pdf_viewer.element_selected(RADIO_BUTTON)

    before_second_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(before_second_zoom_out_scale_factor)
    pdf_viewer.element_selected(RADIO_BUTTON)
