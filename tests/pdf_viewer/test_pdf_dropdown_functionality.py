import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.page_object import GenericPdf

PDF_FILE_NAME = "i-9.pdf"
TYPED_STATE_LETTER = "C"
STATE_SELECTED_BY_TYPED_LETTER = "CA"
FINAL_STATE = "NY"


@pytest.fixture()
def test_case():
    return "1017488"


@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture()
def file_name():
    return PDF_FILE_NAME


def test_pdf_dropdown_selection_with_keyboard_input(
    driver: Firefox,
    pdf_viewer: GenericPdf,
    hard_quit,
):
    """
    Verify that typing inside a PDF form dropdown selects an option based on
    the typed letter, and that the selected option remains after tabbing out.
    """

    # PDF form with dropdown is opened by the pdf_viewer fixture.
    # Step 1: Click on the dropdown field and verify it receives focus.
    dropdown = pdf_viewer.get_element("state-dropdown-field")
    dropdown.click()
    pdf_viewer.expect(lambda _: driver.switch_to.active_element == dropdown)

    # Step 2: Type a letter and verify that the matching option is selected.
    dropdown.send_keys(TYPED_STATE_LETTER)
    pdf_viewer.element_attribute_contains(
        "state-dropdown-field", "value", STATE_SELECTED_BY_TYPED_LETTER
    )

    # Step 3: Select another option from the dropdown.
    final_option = pdf_viewer.select_and_return_dropdown_option(
        "state-dropdown-field", By.XPATH, f"//option[@value='{FINAL_STATE}']"
    )
    pdf_viewer.expect(lambda _: final_option.is_selected())

    # Step 4: Tab out and verify the selection remains.
    dropdown.send_keys(Keys.TAB)
    pdf_viewer.element_attribute_contains("state-dropdown-field", "value", FINAL_STATE)
