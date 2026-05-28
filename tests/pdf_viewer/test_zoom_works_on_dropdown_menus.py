import pytest
from selenium.webdriver.common.by import By

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
DROPDOWN_FIELD = "state-dropdown-field"
DROPDOWN_OPTION = "CA"


@pytest.fixture()
def test_case():
    return "1018758"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_zoom_works_on_dropdown_menus(pdf_viewer: GenericPdf):
    """
    C1018758: Verify that zoom works on dropdown menus
    """
    # Step 1: PDF form with dropdown menus is opened by the pdf_viewer fixture.
    pdf_viewer.element_visible(DROPDOWN_FIELD)

    # Step 2: Click on any dropdown and select any option from it.
    dropdown_option = pdf_viewer.select_and_return_dropdown_option(
        DROPDOWN_FIELD, By.XPATH, f"//option[@value='{DROPDOWN_OPTION}']"
    )
    pdf_viewer.expect(lambda _: dropdown_option.is_selected())

    # Step 3: Zoom in the page and verify there are no unexpected issues with the form.
    before_zoom_in_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_in_toolbar()
    pdf_viewer.expect_scale_factor_greater_than(before_zoom_in_scale_factor)
    pdf_viewer.element_attribute_is(DROPDOWN_FIELD, "value", DROPDOWN_OPTION)

    # Step 4: Zoom out a couple of times and verify there are no unexpected issues with the form.
    before_first_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(before_first_zoom_out_scale_factor)
    pdf_viewer.element_attribute_is(DROPDOWN_FIELD, "value", DROPDOWN_OPTION)

    before_second_zoom_out_scale_factor = float(
        pdf_viewer.pdf_body.value_of_css_property("--scale-factor")
    )

    pdf_viewer.zoom_out_toolbar()
    pdf_viewer.expect_scale_factor_less_than(before_second_zoom_out_scale_factor)
    pdf_viewer.element_attribute_is(DROPDOWN_FIELD, "value", DROPDOWN_OPTION)
