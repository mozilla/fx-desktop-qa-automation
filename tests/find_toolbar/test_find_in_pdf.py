import pytest
from selenium.webdriver import Firefox

from modules.browser_object import FindToolbar
from modules.page_base import BasePage
from modules.page_object import GenericPdf


@pytest.fixture()
def test_case():
    return "127271"


WORD_SEGMENT = "authori"
MATCH_TWO_CONTEXT = "representative must complete"


class element_parent_has_text:
    """
    Custom WebDriverWait event:
     if an element's parent node contains certain text, return the element (not the parent)"""

    def __init__(self, pom: BasePage, name: str, text: str):
        self.name = name
        self.pom = pom
        self.text = text

    def __call__(self, driver: Firefox):
        child = self.pom.get_element(self.name)
        parent = self.pom.get_parent_of(self.name)
        if self.text in parent.text:
            return child
        else:
            return False


def test_find_in_pdf_using_key_combos(
    driver: Firefox, fillable_pdf_url: str, find_toolbar: FindToolbar
):
    """
    C127271: Search on a PDF page

    Arguments:
        fillable_pdf_url: url of the fillable pdf.
        find_toolbar: instantiation of FindToolbar BOM.
    """
    pdf = GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    find_toolbar.open_with_key_combo()
    find_toolbar.find(WORD_SEGMENT)
    assert pdf.get_green_highlighted_text() == WORD_SEGMENT

    find_toolbar.rewind_to_first_match()
    find_toolbar.navigate_matches_by_keys()
    pdf.expect(element_parent_has_text(pdf, "highlighted-text", MATCH_TWO_CONTEXT))
